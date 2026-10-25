package com.example.autotest.reconciliation;

import net.serenitybdd.annotations.Epic;
import net.serenitybdd.annotations.Feature;
import net.serenitybdd.annotations.Steps;
import net.serenitybdd.annotations.Story;
import net.serenitybdd.annotations.Title;
import net.serenitybdd.junit5.SerenityJUnit5Extension;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;

@ExtendWith(SerenityJUnit5Extension.class)
@Epic("交易对账")
@Feature("日终批处理")
@Story("执行日终对账")
@Tag("demo")
class ReconciliationStoryTest {

    @Steps
    ReconciliationSupport reconciliation;

    @Test
    @Title("日终对账成功")
    @Tag("smoke")
    void shouldReconcilePendingTransactions() throws Exception {
        reconciliation.reset();
        reconciliation.insertPendingTransactions(3);
        reconciliation.runConfiguredBatch();

        reconciliation.batchShouldFinishWithExitCode(0);
        reconciliation.logShouldContain("RECONCILIATION COMPLETED");
        reconciliation.logShouldNotContain("ERROR");
        reconciliation.summaryShouldHaveCount(1);
        reconciliation.transactionsShouldHaveStatus("RECONCILED", 3);
    }

    @Test
    @Title("日终对账失败")
    @Tag("negative")
    void shouldKeepTransactionsPendingWhenBatchFails() throws Exception {
        reconciliation.reset();
        reconciliation.insertPendingTransactions(3);
        reconciliation.runBatch("FAIL");

        reconciliation.batchShouldFinishWithExitCode(2);
        reconciliation.logShouldContain("RECONCILIATION FAILED");
        reconciliation.summaryShouldHaveCount(0);
        reconciliation.transactionsShouldHaveStatus("PENDING", 3);
    }
}
