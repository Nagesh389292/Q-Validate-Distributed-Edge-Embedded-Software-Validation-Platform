# Q-Validate AWS Resource Cleanup Script
# Safely tears down temporary AWS EKS, NodeGroup, ECR, and ALB Load Balancer resources created for Q-Validate

param (
    [string]$ClusterName = "qvalidate-eks-cluster",
    [string]$Region = "us-west-2"
)

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " Q-Validate AWS Resource Teardown & Cost Safety Script " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Ask for explicit user confirmation before deleting billable resources
$confirm = Read-Host "Are you sure you want to delete AWS EKS cluster '$ClusterName' in region '$Region'? (y/N)"
if ($confirm -ne 'y' -and $confirm -ne 'Y') {
    Write-Host "Teardown cancelled by user." -ForegroundColor Yellow
    exit 0
}

# 2. Delete EKS Ingress Load Balancer resources first
Write-Host "[1/4] Deleting AWS Ingress & Services..." -ForegroundColor Green
kubectl delete -f k8s/aws/aws-ingress.yaml --ignore-not-found=true
kubectl delete namespace qvalidate-system --ignore-not-found=true

# 3. Delete EKS Cluster via eksctl
Write-Host "[2/4] Deleting EKS Cluster '$ClusterName' via eksctl..." -ForegroundColor Green
eksctl delete cluster --name $ClusterName --region $Region --wait

# 4. Delete ECR Repositories
Write-Host "[3/4] Deleting ECR Repositories..." -ForegroundColor Green
$repos = @("qvalidate-fastapi", "qvalidate-go-scheduler", "qvalidate-cxx-device", "qvalidate-frontend")
foreach ($repo in $repos) {
    Write-Host "Deleting ECR repo: $repo"
    aws ecr delete-repository --repository-name $repo --region $Region --force 2>$null
}

# 5. Clean local kubeconfig context
Write-Host "[4/4] Cleaning local kubectl context..." -ForegroundColor Green
kubectl config delete-context "arn:aws:eks:${Region}:*:cluster/${ClusterName}" 2>$null

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " All Q-Validate AWS Resources Teardown Complete! " -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Cyan
