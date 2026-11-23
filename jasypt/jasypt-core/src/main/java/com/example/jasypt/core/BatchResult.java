package com.example.jasypt.core;

/**
 * 批量加解密中单条输入的处理结果。
 *
 * <p>{@link #getIndex()} 与输入列表的下标一一对应；成功时 {@link #getValue()} 为结果，
 * 失败时 {@link #getError()} 为失败原因。</p>
 */
public final class BatchResult {

    private final int index;
    private final boolean success;
    private final String value;
    private final String error;

    private BatchResult(int index, boolean success, String value, String error) {
        this.index = index;
        this.success = success;
        this.value = value;
        this.error = error;
    }

    static BatchResult success(int index, String value) {
        return new BatchResult(index, true, value, null);
    }

    static BatchResult failure(int index, String error) {
        return new BatchResult(index, false, null, error);
    }

    /**
     * @return 该结果对应的输入下标
     */
    public int getIndex() {
        return index;
    }

    /**
     * @return 是否处理成功
     */
    public boolean isSuccess() {
        return success;
    }

    /**
     * @return 成功时的结果，失败时为 {@code null}
     */
    public String getValue() {
        return value;
    }

    /**
     * @return 失败原因，成功时为 {@code null}
     */
    public String getError() {
        return error;
    }
}
