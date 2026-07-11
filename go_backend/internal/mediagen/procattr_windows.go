//go:build windows

package mediagen

import (
    "os/exec"
    "syscall"
)

// configureProc hides the console window ffmpeg/ffprobe would otherwise flash on
// Windows. When lowPriority is set, the process is also started at
// BELOW_NORMAL_PRIORITY_CLASS so bulk frame extraction doesn't hog the CPU.
func configureProc(cmd *exec.Cmd, lowPriority bool) {
    attr := &syscall.SysProcAttr{HideWindow: true}
    if lowPriority {
        attr.CreationFlags = 0x00004000 // BELOW_NORMAL_PRIORITY_CLASS
    }
    cmd.SysProcAttr = attr
}
