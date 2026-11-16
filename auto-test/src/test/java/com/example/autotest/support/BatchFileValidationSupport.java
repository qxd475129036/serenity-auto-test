package com.example.autotest.support;

import cn.hutool.core.collection.LineIter;
import cn.hutool.core.io.FileUtil;
import cn.hutool.core.io.IORuntimeException;
import cn.hutool.core.io.IoUtil;
import cn.hutool.core.text.csv.CsvReadConfig;
import cn.hutool.core.text.csv.CsvReader;
import cn.hutool.core.text.csv.CsvRow;
import cn.hutool.core.text.csv.CsvUtil;
import cn.hutool.core.util.StrUtil;
import cn.hutool.poi.excel.ExcelReader;
import cn.hutool.poi.excel.ExcelUtil;
import net.serenitybdd.annotations.Step;
import org.apache.poi.ss.usermodel.DataFormatter;
import org.apache.poi.ss.usermodel.FormulaEvaluator;
import org.apache.poi.ss.usermodel.Row;
import org.apache.poi.ss.usermodel.Sheet;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.StringReader;
import java.io.UncheckedIOException;
import java.nio.file.Path;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Deque;
import java.util.List;
import java.util.Locale;

import static org.assertj.core.api.Assertions.assertThat;

public class BatchFileValidationSupport {

    private static final int MAX_LINE_LENGTH = 8192;
    private static final int MAX_DIAGNOSTIC_LINE_LENGTH = 300;
    private static final int DIAGNOSTIC_HEAD_LINES = 10;
    private static final int DIAGNOSTIC_TAIL_LINES = 10;
    private static final int MAX_DIAGNOSTIC_LENGTH = 6000;

    public BatchFileValidationSupport() {
    }

    @Step("日志文件 {0} 应包含: {1}")
    public void logShouldContain(Path file, String expected) {
        assertTextContains(file, expected, "日志");
    }

    @Step("日志文件 {0} 不应包含: {1}")
    public void logShouldNotContain(Path file, String unexpected) {
        assertTextNotContains(file, unexpected, "日志");
    }

    @Step("文本文件 {0} 应包含: {1}")
    public void textFileShouldContain(Path file, String expected) {
        assertTextContains(file, expected, "文本");
    }

    @Step("文本文件 {0} 不应包含: {1}")
    public void textFileShouldNotContain(Path file, String unexpected) {
        assertTextNotContains(file, unexpected, "文本");
    }

    @Step("CSV 文件 {0} 第 {1} 行第 {2} 列应为: {3}")
    public void csvCellShouldEqual(Path file, int rowNumber, int columnNumber, String expected) {
        List<List<String>> rows = readCsv(file);
        String subject = "CSV 文件 " + display(file);
        String actual = cellAt(rows, rowNumber, columnNumber, subject);
        assertThat(actual)
                .as("%s 单元格与预期不符\n行: %d\n列: %d", subject, rowNumber, columnNumber)
                .isEqualTo(expected);
    }

    @Step("CSV 文件 {0} 的全部行应为: {1}")
    public void csvRowsShouldEqual(Path file, List<List<String>> expectedRows) {
        assertThat(readCsv(file))
                .as("CSV 文件整表内容与预期不符\n文件: %s", display(file))
                .isEqualTo(expectedRows);
    }

    @Step("XLSX 文件 {0} 的工作表 {1} 第 {2} 行第 {3} 列应为: {4}")
    public void xlsxCellShouldEqual(Path file, String sheetName,
            int rowNumber, int columnNumber, String expected) {
        List<List<String>> rows = readXlsxRows(file, sheetName);
        String subject = "XLSX 文件 " + display(file) + " 工作表 " + sheetName;
        String actual = cellAt(rows, rowNumber, columnNumber, subject);
        assertThat(actual)
                .as("%s 单元格与预期不符\n行: %d\n列: %d", subject, rowNumber, columnNumber)
                .isEqualTo(expected);
    }

    @Step("XLSX 文件 {0} 的工作表 {1} 全部行应为: {2}")
    public void xlsxRowsShouldEqual(Path file, String sheetName,
            List<List<String>> expectedRows) {
        assertThat(readXlsxRows(file, sheetName))
                .as("XLSX 文件整表内容与预期不符\n文件: %s\n工作表: %s", display(file), sheetName)
                .isEqualTo(expectedRows);
    }

    private void assertTextContains(Path file, String expected, String fileType) {
        TextScan scan = scanText(file, expected, fileType);
        assertThat(scan.matched())
                .as(missingContentMessage(fileType, file, expected, scan))
                .isTrue();
    }

    private void assertTextNotContains(Path file, String unexpected, String fileType) {
        TextScan scan = scanText(file, unexpected, fileType);
        assertThat(scan.matched())
                .as(unexpectedContentMessage(fileType, file, unexpected, scan))
                .isFalse();
    }

    private TextScan scanText(Path file, String needle, String fileType) {
        Path path = requireRegularFile(file);
        long totalBytes = FileUtil.size(path.toFile());
        int windowSize = StrUtil.split(needle, '\n', -1, false, false).size();
        List<String> headLines = new ArrayList<>(DIAGNOSTIC_HEAD_LINES);
        Deque<String> tailLines = new ArrayDeque<>(DIAGNOSTIC_TAIL_LINES);
        Deque<String> window = new ArrayDeque<>(windowSize);
        long lineNumber = 0;
        long matchLine = 0;
        String matchLineText = null;

        try (LineIter lines = IoUtil.lineIter(FileUtil.getUtf8Reader(path.toFile()))) {
            while (lines.hasNext()) {
                String line = lines.next();
                lineNumber++;
                String diagnosticLine = StrUtil.maxLength(line, MAX_DIAGNOSTIC_LINE_LENGTH);
                if (headLines.size() < DIAGNOSTIC_HEAD_LINES) {
                    headLines.add(diagnosticLine);
                }
                if (tailLines.size() == DIAGNOSTIC_TAIL_LINES) {
                    tailLines.removeFirst();
                }
                tailLines.addLast(diagnosticLine);

                window.addLast(limit(line, MAX_LINE_LENGTH));
                if (window.size() > windowSize) {
                    window.removeFirst();
                }
                boolean matched = windowSize == 1
                        ? StrUtil.contains(line, needle)
                        : window.size() == windowSize
                                && StrUtil.contains(StrUtil.join("\n", window), needle);
                if (matched) {
                    matchLine = lineNumber - windowSize + 1;
                    matchLineText = diagnosticLine;
                    break;
                }
            }
        } catch (IORuntimeException exception) {
            throw new UncheckedIOException("无法读取" + fileType + "文件: " + path,
                    new IOException(exception));
        }
        return new TextScan(lineNumber, totalBytes, matchLine, matchLineText,
                List.copyOf(headLines), List.copyOf(tailLines));
    }

    private String missingContentMessage(String fileType, Path file, String expected, TextScan scan) {
        return StrUtil.maxLength(StrUtil.format("""
                {}文件缺少预期内容
                文件: {}
                预期包含: {}
                总行数: {}
                文件大小: {} 字节
                前 {} 行:
                {}
                后 {} 行:
                {}""",
                fileType, display(file), expected, scan.totalLines(), scan.totalBytes(),
                scan.headLines().size(), excerpt(scan.headLines()),
                scan.tailLines().size(), excerpt(scan.tailLines())),
                MAX_DIAGNOSTIC_LENGTH);
    }

    private String unexpectedContentMessage(String fileType, Path file, String unexpected, TextScan scan) {
        return StrUtil.maxLength(StrUtil.format("""
                {}文件包含异常内容
                文件: {}
                不应包含: {}
                首次出现行号: {}
                该行内容: {}
                已扫描行数: {}
                文件大小: {} 字节
                前 {} 行:
                {}""",
                fileType, display(file), unexpected, scan.matchLine(), scan.matchLineText(),
                scan.totalLines(), scan.totalBytes(),
                scan.headLines().size(), excerpt(scan.headLines())),
                MAX_DIAGNOSTIC_LENGTH);
    }

    private String excerpt(List<String> lines) {
        return StrUtil.join("\n", lines);
    }

    private String limit(String text, int maxLength) {
        return text.length() <= maxLength ? text : StrUtil.sub(text, 0, maxLength);
    }

    private List<List<String>> readCsv(Path file) {
        Path path = requireRegularFile(file);
        String content;
        try (BufferedReader reader = FileUtil.getBOMReader(path.toFile())) {
            content = IoUtil.read(reader);
        } catch (IOException exception) {
            throw new UncheckedIOException("无法读取CSV文件: " + path, exception);
        }
        assertCsvQuotesBalanced(content, path);

        CsvReadConfig config = CsvReadConfig.defaultConfig()
                .setSkipEmptyRows(false)
                .setTrimField(false)
                .setErrorOnDifferentFieldCount(false);
        try (CsvReader reader = CsvUtil.getReader(new StringReader(content), config)) {
            return reader.read().getRows().stream()
                    .map(CsvRow::getRawList)
                    .map(List::copyOf)
                    .toList();
        } catch (IOException exception) {
            throw new UncheckedIOException("无法解析CSV文件: " + path, exception);
        }
    }

    private void assertCsvQuotesBalanced(String content, Path path) {
        boolean inQuotes = false;
        boolean atFieldStart = true;
        for (int index = 0; index < content.length(); index++) {
            char current = content.charAt(index);
            if (inQuotes) {
                if (current == '"') {
                    if (index + 1 < content.length() && content.charAt(index + 1) == '"') {
                        index++;
                    } else {
                        inQuotes = false;
                        atFieldStart = false;
                    }
                }
                continue;
            }
            if (current == '"' && atFieldStart) {
                inQuotes = true;
                atFieldStart = false;
            } else if (current == ',' || current == '\r' || current == '\n') {
                atFieldStart = true;
            } else {
                atFieldStart = false;
            }
        }
        if (inQuotes) {
            throw new IllegalArgumentException("CSV 文件解析失败，存在未闭合的引号: " + path);
        }
    }

    private List<List<String>> readXlsxRows(Path file, String sheetName) {
        Path path = requireRegularFile(file);
        assertThat(StrUtil.isNotBlank(sheetName))
                .as("XLSX 工作表名称不能为空\n文件: %s", path)
                .isTrue();

        try (ExcelReader reader = openXlsx(path, sheetName)) {
            return extractRows(reader.getSheet());
        }
    }

    private ExcelReader openXlsx(Path path, String sheetName) {
        try {
            return ExcelUtil.getReader(path.toFile(), sheetName);
        } catch (IllegalArgumentException exception) {
            List<String> availableSheets;
            try (ExcelReader workbook = ExcelUtil.getReader(path.toFile())) {
                availableSheets = workbook.getSheetNames();
            }
            throw new AssertionError(StrUtil.format("""
                    XLSX 工作表不存在
                    文件: {}
                    工作表: {}
                    可用工作表: {}""", path, sheetName, availableSheets), exception);
        } catch (IORuntimeException exception) {
            throw new UncheckedIOException("无法读取 XLSX 文件: " + path,
                    new IOException(exception));
        }
    }

    private List<List<String>> extractRows(Sheet sheet) {
        DataFormatter formatter = new DataFormatter(Locale.ROOT);
        FormulaEvaluator evaluator = sheet.getWorkbook().getCreationHelper().createFormulaEvaluator();
        List<List<String>> rows = new ArrayList<>();

        for (int rowIndex = 0; rowIndex <= sheet.getLastRowNum(); rowIndex++) {
            Row row = sheet.getRow(rowIndex);
            int cellCount = row == null ? 0 : Math.max(row.getLastCellNum(), 0);
            List<String> values = new ArrayList<>(cellCount);
            for (int columnIndex = 0; columnIndex < cellCount; columnIndex++) {
                values.add(formatter.formatCellValue(row.getCell(columnIndex), evaluator));
            }
            int contentEnd = values.size();
            while (contentEnd > 0 && values.get(contentEnd - 1).isEmpty()) {
                contentEnd--;
            }
            rows.add(new ArrayList<>(values.subList(0, contentEnd)));
        }
        while (!rows.isEmpty() && rows.get(rows.size() - 1).isEmpty()) {
            rows.remove(rows.size() - 1);
        }
        return rows;
    }

    private String cellAt(List<List<String>> rows, int rowNumber, int columnNumber, String subject) {
        assertThat(rowNumber)
                .as("%s 的行号必须从 1 开始", subject)
                .isGreaterThanOrEqualTo(1);
        assertThat(columnNumber)
                .as("%s 的列号必须从 1 开始", subject)
                .isGreaterThanOrEqualTo(1);
        assertThat(rows.size())
                .as("%s 的第 %d 行不存在，实际共 %d 行", subject, rowNumber, rows.size())
                .isGreaterThanOrEqualTo(rowNumber);

        List<String> row = rows.get(rowNumber - 1);
        assertThat(row.size())
                .as("%s 的第 %d 行第 %d 列不存在，该行实际共 %d 列",
                        subject, rowNumber, columnNumber, row.size())
                .isGreaterThanOrEqualTo(columnNumber);
        return row.get(columnNumber - 1);
    }

    private Path requireRegularFile(Path file) {
        assertThat(file).as("文件路径不能为空").isNotNull();
        Path path = display(file);
        assertThat(FileUtil.isFile(path.toFile()))
                .as(StrUtil.format("文件不存在或不是普通文件: {}", path))
                .isTrue();
        return path;
    }

    private Path display(Path file) {
        return file.toAbsolutePath().normalize();
    }

    private record TextScan(
            long totalLines,
            long totalBytes,
            long matchLine,
            String matchLineText,
            List<String> headLines,
            List<String> tailLines) {

        private boolean matched() {
            return matchLine > 0;
        }
    }
}
