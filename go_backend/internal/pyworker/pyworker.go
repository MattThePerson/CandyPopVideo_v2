package pyworker

import (
    "encoding/json"
    "fmt"
    "log"
    "os"
    "os/exec"
    "path/filepath"
    "runtime"
    "sync"
    "time"
)

var (
    rootOnce sync.Once
    rootPath string
)

// Root returns the absolute path to the py/ directory. It searches up from
// both the executable directory (for built binaries) and the working directory
// (for go run), taking the first ancestor that contains py/.venv/.
// Calls log.Fatal if py/.venv is not found.
func Root() string {
    rootOnce.Do(findRoot)
    return rootPath
}

// Interpreter returns the Python executable inside py/.venv.
func Interpreter() string {
    if runtime.GOOS == "windows" {
        return filepath.Join(Root(), ".venv", "Scripts", "python.exe")
    }
    return filepath.Join(Root(), ".venv", "bin", "python3")
}

// Exec runs args as a Python subprocess with cwd=py/. Returns elapsed seconds.
func Exec(args ...string) (float64, error) {
    start := time.Now()
    cmd := exec.Command(Interpreter(), args...)
    cmd.Dir = Root()
    if output, err := cmd.CombinedOutput(); err != nil {
        log.Printf("STDOUT\n****\n%s\n****", string(output))
        return -1, err
    }
    return time.Since(start).Seconds(), nil
}

// ExecOutput runs args as a Python subprocess with cwd=py/, and parses the
// combined stdout as JSON into R.
func ExecOutput[R any](args ...string) (R, error) {
    var reply R
    cmd := exec.Command(Interpreter(), args...)
    cmd.Dir = Root()
    output, err := cmd.CombinedOutput()
    if err != nil {
        log.Printf("STDOUT\n****\n%s\n****", string(output))
        return reply, err
    }
    if err := json.Unmarshal(output, &reply); err != nil {
        return reply, fmt.Errorf("parsing subprocess JSON: %w — output: %s", err, string(output))
    }
    return reply, nil
}

// findRoot populates rootPath by walking up from the executable dir and cwd.
func findRoot() {
    var starts []string

    if exe, err := os.Executable(); err == nil {
        if real, err := filepath.EvalSymlinks(exe); err == nil {
            starts = append(starts, filepath.Dir(real))
        } else {
            starts = append(starts, filepath.Dir(exe))
        }
    }
    if cwd, err := os.Getwd(); err == nil {
        starts = append(starts, cwd)
    }

    for _, start := range starts {
        dir := start
        for {
            candidate := filepath.Join(dir, "py", ".venv")
            if info, err := os.Stat(candidate); err == nil && info.IsDir() {
                rootPath = filepath.Join(dir, "py")
                return
            }
            parent := filepath.Dir(dir)
            if parent == dir {
                break
            }
            dir = parent
        }
    }

    log.Fatal("[pyworker] could not find py/.venv — run 'uv sync' inside the py/ directory")
}
