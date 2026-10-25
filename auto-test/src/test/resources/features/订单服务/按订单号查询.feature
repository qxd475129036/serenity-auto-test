@demo @cucumber @parallel
# Capability: 订单服务
Feature: 按订单号查询
  作为调用方
  我希望按订单号查询订单
  以便确认订单状态

  Background:
    Given 本地订单服务已启动

  @smoke
  Scenario: 查询存在的订单
    When 我查询订单 1
    Then 订单状态应为 PAID

  @smoke
  Scenario Outline: 按不同订单号查询订单
    When 我查询订单 <id>
    Then 订单状态应为 <status>

    Examples:
      | id | status |
      | 1  | PAID   |
      | 2  | PAID   |

  @negative
  Scenario: 查询不存在的订单
    When 我查询订单 999
    Then 应返回 404 错误
