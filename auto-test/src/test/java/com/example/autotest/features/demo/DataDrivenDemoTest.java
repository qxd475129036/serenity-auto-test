package com.example.autotest.features.demo;

import com.example.autotest.steps.BatchShellSteps;
import com.example.autotest.steps.OracleSteps;
import com.example.autotest.support.BatchCommandResult;
import net.serenitybdd.annotations.Epic;
import net.serenitybdd.annotations.Feature;
import net.serenitybdd.annotations.Steps;
import net.serenitybdd.annotations.Story;
import net.serenitybdd.junit5.SerenityJUnit5Extension;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.extension.ExtendWith;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;

import static org.assertj.core.api.Assertions.assertThat;

@ExtendWith(SerenityJUnit5Extension.class)
@Epic("交易对账")
@Feature("日终对账处理")
@Story("按业务日期对账并得到预期结果")
@Tag("demo")
class DataDrivenDemoTest {

    @Steps
    OracleSteps oracle;

    @Steps
    BatchShellSteps batch;

    @ParameterizedTest(name = "业务日期 {0} 期望退出码 {1}")
    @CsvSource({"2026-10-31, 0", "FAIL, 2"})
    void should_produce_expected_exit_code(String businessDate, int expectedExitCode) throws Exception {
        oracle.reset();
        oracle.insertPendingTransactions(3);

        BatchCommandResult result = batch.runForDate(businessDate);

        assertThat(result.timedOut()).isFalse();
        assertThat(result.exitCode()).isEqualTo(expectedExitCode);
        oracle.summaryShouldHaveCount(expectedExitCode == 0 ? 1 : 0);
        oracle.transactionsShouldHaveStatus(expectedExitCode == 0 ? "RECONCILED" : "PENDING", 3);
    }
}
