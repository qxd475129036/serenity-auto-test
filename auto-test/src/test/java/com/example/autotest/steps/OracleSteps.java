package com.example.autotest.steps;

import com.example.autotest.config.TestSettings;
import net.serenitybdd.annotations.Step;
import org.springframework.core.io.ClassPathResource;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.datasource.DriverManagerDataSource;
import org.springframework.jdbc.datasource.init.ResourceDatabasePopulator;

import java.math.BigDecimal;
import java.util.List;
import java.util.stream.LongStream;

import static org.assertj.core.api.Assertions.assertThat;

public class OracleSteps {

    private final JdbcTemplate jdbcTemplate;

    public OracleSteps() {
        TestSettings settings = new TestSettings();
        DriverManagerDataSource dataSource = new DriverManagerDataSource(
                settings.dbUrl(),
                settings.dbUser(),
                settings.dbPassword());
        if ("h2".equalsIgnoreCase(settings.dbKind())) {
            dataSource.setDriverClassName("org.h2.Driver");
        } else {
            dataSource.setDriverClassName("oracle.jdbc.OracleDriver");
        }
        this.jdbcTemplate = new JdbcTemplate(dataSource);
        if (settings.initializeDatabase()) {
            new ResourceDatabasePopulator(
                    new ClassPathResource("db/reconciliation-schema.sql"))
                    .execute(dataSource);
        }
    }

    @Step("清空上一场景生成的对账测试数据")
    public void reset() {
        jdbcTemplate.update("DELETE FROM reconciliation_summary");
        jdbcTemplate.update("DELETE FROM transactions");
    }

    @Step("向 TRANSACTIONS 预置 {0} 笔待对账交易")
    public void insertPendingTransactions(int count) {
        String sql = "INSERT INTO transactions(id, status, amount) VALUES(?, 'PENDING', ?)";
        List<Long> transactionIds = LongStream.rangeClosed(1, count).boxed().toList();
        jdbcTemplate.batchUpdate(
                sql,
                transactionIds,
                count,
                (statement, transactionId) -> {
                    statement.setLong(1, transactionId);
                    statement.setBigDecimal(2, new BigDecimal("100.00"));
                });
    }

    @Step("汇总表中应有 {0} 条对账记录")
    public void summaryShouldHaveCount(int expected) {
        Integer actual = jdbcTemplate.queryForObject(
                "SELECT COUNT(*) FROM reconciliation_summary",
                Integer.class);
        assertThat(actual).isEqualTo(expected);
    }

    @Step("应存在 {1} 笔状态为 {0} 的交易")
    public void transactionsShouldHaveStatus(String status, int expected) {
        Integer actual = jdbcTemplate.queryForObject(
                "SELECT COUNT(*) FROM transactions WHERE status = ?",
                Integer.class,
                status);
        assertThat(actual).isEqualTo(expected);
    }
}
