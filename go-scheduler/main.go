package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"sync"
	"time"
)

type Device struct {
	ID           string   `json:"device_id"`
	Name         string   `json:"name"`
	Capabilities []string `json:"capabilities"`
	IsReserved   bool     `json:"is_reserved"`
}

type TestJob struct {
	JobID              string   `json:"job_id"`
	TestID             string   `json:"test_id"`
	RequiredCapability string   `json:"required_capability"`
	Priority           int      `json:"priority"`
	Status             string   `json:"status"`
	AllocatedDeviceID  string   `json:"allocated_device_id"`
	CreatedAt          time.Time `json:"created_at"`
}

type Scheduler struct {
	mu      sync.Mutex
	devices map[string]*Device
	queue   []*TestJob
}

func NewScheduler() *Scheduler {
	s := &Scheduler{
		devices: make(map[string]*Device),
		queue:   make([]*TestJob, 0),
	}

	// Initialize 10 Simulated Edge Nodes with Capability Profiles
	s.devices["DEVICE-001"] = &Device{ID: "DEVICE-001", Name: "Snapdragon Alpha", Capabilities: []string{"CPU", "MEMORY", "AI_ACCELERATOR"}}
	s.devices["DEVICE-002"] = &Device{ID: "DEVICE-002", Name: "Hexagon DSP Sim", Capabilities: []string{"CPU", "MEMORY", "DSP"}}
	s.devices["DEVICE-003"] = &Device{ID: "DEVICE-003", Name: "Cloud Edge Gateway", Capabilities: []string{"CPU", "MEMORY", "NETWORK"}}
	s.devices["DEVICE-004"] = &Device{ID: "DEVICE-004", Name: "Hexagon AI/DSP Node", Capabilities: []string{"CPU", "MEMORY", "DSP", "AI_ACCELERATOR"}}

	return s
}

func (s *Scheduler) SubmitJobHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method Not Allowed", http.StatusMethodNotAllowed)
		return
	}

	var job TestJob
	if err := json.NewDecoder(r.Body).Decode(&job); err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	job.JobID = fmt.Sprintf("GO-JOB-%d", time.Now().UnixNano())
	job.Status = "QUEUED"
	job.CreatedAt = time.Now()

	s.mu.Lock()
	s.queue = append(s.queue, &job)
	s.mu.Unlock()

	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(job)
}

func (s *Scheduler) StatusHandler(w http.ResponseWriter, r *http.Request) {
	s.mu.Lock()
	defer s.mu.Unlock()

	res := map[string]interface{}{
		"platform":       "Q-Validate Go Distributed Test Scheduler v4.0",
		"queue_depth":    len(s.queue),
		"device_count":   len(s.devices),
		"status":         "RUNNING",
	}

	json.NewEncoder(w).Encode(res)
}

func main() {
	scheduler := NewScheduler()

	http.HandleFunc("/api/v1/scheduler/submit", scheduler.SubmitJobHandler)
	http.HandleFunc("/api/v1/scheduler/status", scheduler.StatusHandler)

	fmt.Println("========================================================")
	fmt.Println("   Q-Validate — Go Distributed Test Scheduler Service   ")
	fmt.Println("========================================================")
	fmt.Println("[INFO] Go Scheduler Listening on :8080...")

	log.Fatal(http.ListenAndServe(":8080", nil))
}
