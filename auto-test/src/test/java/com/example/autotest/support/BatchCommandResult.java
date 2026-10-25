package com.example.autotest.support;

public record BatchCommandResult(
        int exitCode,
        String stdout,
        String stderr,
        boolean timedOut) {

    public String diagnosticText() {
        return """
                exitCode=%d, timedOut=%s
                stdout:
                %s
                stderr:
                %s
                """.formatted(exitCode, timedOut, stdout, stderr);
    }
}
