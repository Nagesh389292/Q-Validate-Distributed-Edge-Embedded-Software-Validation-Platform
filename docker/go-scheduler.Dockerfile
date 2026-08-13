FROM golang:1.22-alpine AS builder
WORKDIR /app
COPY main.go .
RUN go mod init qvalidate/scheduler && go build -o scheduler main.go

FROM alpine:latest
WORKDIR /app
COPY --from=builder /app/scheduler .
EXPOSE 8080
CMD ["./scheduler"]
