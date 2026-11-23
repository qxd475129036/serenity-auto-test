package com.example.autotest.reconciliation;

import org.junit.jupiter.api.Test;

import static org.assertj.core.api.Assertions.assertThatThrownBy;

class ReconciliationSupportTest {

    @Test
    void shouldIsolateLogPerBatchRun() throws Exception {
        ReconciliationSupport support = new ReconciliationSupport();
        support.reset();
        support.insertPendingTransactions(1);

        support.runBatch("2026-10-31");
        support.batchShouldFinishWithExitCode(0);
        support.logShouldContain("RECONCILIATION COMPLETED");

        support.runBatch("FAIL");
        support.batchShouldFinishWithExitCode(2);

        assertThatThrownBy(() -> support.logShouldContain("RECONCILIATION COMPLETED"))
                .isInstanceOf(AssertionError.class)
                .hasMessageContainingAll("日志文件缺少预期内容", "RECONCILIATION FAILED")
                .hasMessageNotContaining("{:02d}");
    }
}
