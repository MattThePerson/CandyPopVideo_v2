//go:build !windows

package mediagen

import "os/exec"

// configureProc is a no-op on non-Windows platforms; HideWindow and
// CreationFlags only exist in syscall.SysProcAttr on Windows.
func configureProc(cmd *exec.Cmd, lowPriority bool) {}
