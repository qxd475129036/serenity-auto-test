package com.example.autotest.features.batch;

import com.example.autotest.config.TestSettings;
import com.example.autotest.steps.BatchShellSteps;
import com.example.autotest.steps.LogAssertionSteps;
import com.example.autotest.steps.OracleSteps;
import com.example.autotest.support.BatchCommandResult;
import net.serenitybdd.annotations.Epic;
import net.serenitybdd.annotations.Feature;
import net.serenitybdd.annotations.Steps;
import net.serenitybdd.annotations.Story;
import net.serenitybdd.junit5.SerenityJUnit5Extension;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;

@ExtendWith(SerenityJUnit5Extension.class)
@Epic("交易对账")
@Feature("日终对账处理")
@Story("对账成功后状态与汇总正确")
class ReconciliationBatchTest {

    private final TestSettings settings = new TestSettings();

    @Steps
    OracleSteps oracle;

    @Steps
    BatchShellSteps batch;

    @Steps
    LogAssertionSteps logs;

    @Test
    @Tag("smoke")
    void should_reconcile_pending_transactions_and_generate_summary() throws Exception {
        oracle.reset();
        oracle.insertPendingTransactions(3);

        BatchCommandResult result = batch.runForDate(settings.batchDate());

        batch.shouldSucceed(result);
        logs.logShouldContain(settings.batchLogFile(), "RECONCILIATION COMPLETED");
        logs.logShouldNotContain(settings.batchLogFile(), "ERROR");
        oracle.summaryShouldHaveCount(1);
        oracle.transactionsShouldHaveStatus("RECONCILED", 3);
    }
}
