package com.example.autotest.support;

import cn.hutool.core.io.FileUtil;
import org.apache.poi.ss.usermodel.Row;
import org.apache.poi.ss.usermodel.Sheet;
import org.apache.poi.ss.usermodel.Workbook;
import org.apache.poi.xssf.usermodel.XSSFWorkbook;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

import java.io.BufferedWriter;
import java.io.IOException;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.function.IntFunction;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.assertj.core.api.Assertions.catchThrowable;

class BatchFileValidationSupportTest {

    private final BatchFileValidationSupport validation = new BatchFileValidationSupport();

    @TempDir
    Path tempDir;

    @Test
    void shouldValidateLogAndTextContent() throws IOException {
        Path log = writeText("batch.log", "START\nRECONCILIATION COMPLETED\n");
        Path text = writeText("notes.txt", "第一行\nSecond Line\n");

        validation.logShouldContain(log, "RECONCILIATION COMPLETED");
        validation.logShouldNotContain(log, "ERROR");
        validation.textFileShouldContain(text, "第一行\nSecond");
        validation.textFileShouldNotContain(text, "second line");
    }

    @Test
    void shouldReportTextAssertionFailuresWithFileContext() throws IOException {
        Path log = writeText("failure.log", "START\nFAILED\n");
        Path text = writeText("failure.txt", "first line\nERROR occurred\n");

        assertThatThrownBy(() -> validation.logShouldContain(log, "COMPLETED"))
                .isInstanceOf(AssertionError.class)
                .hasMessageContainingAll(log.toString(), "COMPLETED", "START", "FAILED");
        assertThatThrownBy(() -> validation.textFileShouldNotContain(text, "ERROR"))
                .isInstanceOf(AssertionError.class)
                .hasMessageContainingAll(text.toString(), "ERROR", "first line");
    }

    @Test
    void shouldValidateCsvCellsAndRowsWithQuotedContent() throws IOException {
        Path csv = writeText("quoted.csv",
                "\uFEFF编号,备注,值\r\n"
                        + "1,\"上海,浦东\",\"他说\"\"好\"\"\"\r\n"
                        + "2,\"第一行\n第二行\",100\r\n");
        List<List<String>> expectedRows = List.of(
                List.of("编号", "备注", "值"),
                List.of("1", "上海,浦东", "他说\"好\""),
                List.of("2", "第一行\n第二行", "100"));

        validation.csvRowsShouldEqual(csv, expectedRows);
        validation.csvCellShouldEqual(csv, 2, 2, "上海,浦东");
        validation.csvCellShouldEqual(csv, 2, 3, "他说\"好\"");
        validation.csvCellShouldEqual(csv, 3, 2, "第一行\n第二行");
    }

    @Test
    void shouldReportCsvDifferencesAndInvalidCoordinates() throws IOException {
        Path csv = writeText("coordinates.csv", "A,B\n1,2\n");

        assertThatThrownBy(() -> validation.csvRowsShouldEqual(csv,
                List.of(List.of("1", "2"), List.of("A", "B"))))
                .isInstanceOf(AssertionError.class)
                .hasMessageContainingAll(csv.toString(), "A", "1");
        assertThatThrownBy(() -> validation.csvCellShouldEqual(csv, 2, 2, "3"))
                .isInstanceOf(AssertionError.class)
                .hasMessageContainingAll(csv.toString(), "行: 2", "列: 2", "3", "2");
        assertThatThrownBy(() -> validation.csvCellShouldEqual(csv, 0, 1, "A"))
                .isInstanceOf(AssertionError.class)
                .hasMessageContaining("行号必须从 1 开始");
        assertThatThrownBy(() -> validation.csvCellShouldEqual(csv, 3, 1, "A"))
                .isInstanceOf(AssertionError.class)
                .hasMessageContainingAll("第 3 行不存在", "实际共 2 行");
    }

    @Test
    void shouldReportMalformedCsvWithFileContext() throws IOException {
        Path csv = writeText("malformed.csv", "A,B\n1,\"未闭合");

        assertThatThrownBy(() -> validation.csvRowsShouldEqual(csv, List.of()))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessageContainingAll("CSV 文件解析失败", "未闭合", csv.toString());
    }

    @Test
    void shouldValidateXlsxCellsAndRowsUsingDisplayedValues() throws IOException {
        Path xlsx = tempDir.resolve("result.xlsx");
        createXlsx(xlsx);
        List<List<String>> expectedRows = List.of(
                List.of("订单号", "金额", "已核对", "合计"),
                List.of("ORD-1", "100", "TRUE", "3"));

        validation.xlsxRowsShouldEqual(xlsx, "对账结果", expectedRows);
        validation.xlsxCellShouldEqual(xlsx, "对账结果", 2, 1, "ORD-1");
        validation.xlsxCellShouldEqual(xlsx, "对账结果", 2, 2, "100");
        validation.xlsxCellShouldEqual(xlsx, "对账结果", 2, 3, "TRUE");
        validation.xlsxCellShouldEqual(xlsx, "对账结果", 2, 4, "3");
    }

    @Test
    void shouldReportXlsxDifferencesAndInvalidSheetOrCoordinates() throws IOException {
        Path xlsx = tempDir.resolve("failure.xlsx");
        createXlsx(xlsx);

        assertThatThrownBy(() -> validation.xlsxRowsShouldEqual(xlsx, "缺失", List.of()))
                .isInstanceOf(AssertionError.class)
                .hasMessageContainingAll(xlsx.toString(), "工作表不存在", "缺失", "对账结果");
        assertThatThrownBy(() -> validation.xlsxCellShouldEqual(
                xlsx, "对账结果", 1, 1, "错误"))
                .isInstanceOf(AssertionError.class)
                .hasMessageContainingAll(xlsx.toString(), "对账结果", "行: 1", "列: 1", "错误", "订单号");
        assertThatThrownBy(() -> validation.xlsxRowsShouldEqual(
                xlsx, "对账结果", List.of(List.of("错误"))))
                .isInstanceOf(AssertionError.class)
                .hasMessageContainingAll(xlsx.toString(), "对账结果", "错误", "订单号");
        assertThatThrownBy(() -> validation.xlsxCellShouldEqual(
                xlsx, "对账结果", 1, 0, "订单号"))
                .isInstanceOf(AssertionError.class)
                .hasMessageContaining("列号必须从 1 开始");
    }

    @Test
    void shouldRejectMissingOrNonRegularFilesForEveryFormat() throws IOException {
        Path missingLog = tempDir.resolve("missing.log");
        Path directoryText = Files.createDirectory(tempDir.resolve("directory.txt"));
        Path missingCsv = tempDir.resolve("missing.csv");
        Path directoryXlsx = Files.createDirectory(tempDir.resolve("directory.xlsx"));

        assertThatThrownBy(() -> validation.logShouldContain(missingLog, "START"))
                .isInstanceOf(AssertionError.class)
                .hasMessageContainingAll("文件不存在或不是普通文件", missingLog.toString());
        assertThatThrownBy(() -> validation.textFileShouldContain(directoryText, "text"))
                .isInstanceOf(AssertionError.class)
                .hasMessageContainingAll("文件不存在或不是普通文件", directoryText.toString());
        assertThatThrownBy(() -> validation.csvRowsShouldEqual(missingCsv, List.of()))
                .isInstanceOf(AssertionError.class)
                .hasMessageContainingAll("文件不存在或不是普通文件", missingCsv.toString());
        assertThatThrownBy(() -> validation.xlsxRowsShouldEqual(directoryXlsx, "sheet", List.of()))
                .isInstanceOf(AssertionError.class)
                .hasMessageContainingAll("文件不存在或不是普通文件", directoryXlsx.toString());
    }

    @Test
    void shouldValidateLargeLogWithBoundedDiagnostics() throws IOException {
        Path log = writeLines("large.log", 50_000,
                lineNumber -> lineNumber == 50_000
                        ? "RECONCILIATION COMPLETED"
                        : "RECONCILIATION STARTED i=" + lineNumber);

        validation.logShouldContain(log, "RECONCILIATION COMPLETED");
        validation.logShouldNotContain(log, "ERROR");

        Throwable failure = catchThrowable(
                () -> validation.logShouldContain(log, "NEVER-PRESENT"));
        assertThat(failure).isInstanceOf(AssertionError.class);
        assertThat(failure.getMessage())
                .contains(log.toString(), "预期包含: NEVER-PRESENT", "总行数: 50000")
                .hasSizeLessThan(8000);
    }

    @Test
    void shouldReportFirstMatchingLineForForbiddenContent() throws IOException {
        Path log = writeLines("forbidden.log", 20_000,
                lineNumber -> lineNumber == 15_000
                        ? "ERROR at line " + lineNumber
                        : "INFO line " + lineNumber);

        Throwable failure = catchThrowable(
                () -> validation.logShouldNotContain(log, "ERROR"));
        assertThat(failure).isInstanceOf(AssertionError.class);
        assertThat(failure.getMessage())
                .contains("首次出现行号: 15000", "ERROR at line 15000")
                .hasSizeLessThan(8000);
    }

    @Test
    void shouldMatchMultiLineTextAcrossCrlfLines() {
        Path text = writeText("crlf.txt", "第一行\r\nSecond\r\n");

        validation.textFileShouldContain(text, "第一行\nSecond");
    }

    @Test
    void shouldMatchTailOfOversizedSingleLine() {
        Path log = writeText("long-line.log", "A".repeat(20_000) + "TAIL\n");

        validation.logShouldContain(log, "TAIL");

        Throwable failure = catchThrowable(
                () -> validation.logShouldContain(log, "NEVER-PRESENT"));
        assertThat(failure).isInstanceOf(AssertionError.class);
        assertThat(failure.getMessage())
                .contains(log.toString(), "总行数: 1")
                .hasSizeLessThan(8000);
    }

    private Path writeLines(String name, int lineCount, IntFunction<String> lineFactory)
            throws IOException {
        Path file = tempDir.resolve(name);
        try (BufferedWriter writer = FileUtil.getWriter(
                file.toFile(), StandardCharsets.UTF_8, false)) {
            for (int lineNumber = 1; lineNumber <= lineCount; lineNumber++) {
                writer.write(lineFactory.apply(lineNumber));
                writer.newLine();
            }
        }
        return file;
    }

    private Path writeText(String name, String content) {
        return FileUtil.writeUtf8String(content, tempDir.resolve(name).toFile()).toPath();
    }

    private void createXlsx(Path file) throws IOException {
        try (Workbook workbook = new XSSFWorkbook()) {
            Sheet sheet = workbook.createSheet("对账结果");
            Row header = sheet.createRow(0);
            header.createCell(0).setCellValue("订单号");
            header.createCell(1).setCellValue("金额");
            header.createCell(2).setCellValue("已核对");
            header.createCell(3).setCellValue("合计");

            Row data = sheet.createRow(1);
            data.createCell(0).setCellValue("ORD-1");
            data.createCell(1).setCellValue(100);
            data.createCell(2).setCellValue(true);
            data.createCell(3).setCellFormula("1+2");
            data.createCell(4).setCellValue("");
            sheet.createRow(2).createCell(0).setCellValue("");

            try (OutputStream output = Files.newOutputStream(file)) {
                workbook.write(output);
            }
        }
    }
}
