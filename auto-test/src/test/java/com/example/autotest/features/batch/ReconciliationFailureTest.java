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
@Story("批处理失败时保持原数据")
class ReconciliationFailureTest {

    private final TestSettings settings = new TestSettings();

    @Steps
    OracleSteps oracle;

    @Steps
    BatchShellSteps batch;

    @Steps
    LogAssertionSteps logs;

    @Test
    @Tag("negative")
    void should_leave_pending_transactions_unchanged_when_batch_fails() throws Exception {
        oracle.reset();
        oracle.insertPendingTransactions(3);

        BatchCommandResult result = batch.runForDate("FAIL");

        batch.shouldFailWith(result, 2);
        logs.logShouldContain(settings.batchLogFile(), "RECONCILIATION FAILED");
        oracle.summaryShouldHaveCount(0);
        oracle.transactionsShouldHaveStatus("PENDING", 3);
    }
}
