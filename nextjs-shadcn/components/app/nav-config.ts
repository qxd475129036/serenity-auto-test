import {
  BadgeCheckIcon,
  ClipboardListIcon,
  DownloadIcon,
  FileInputIcon,
  FileTextIcon,
  HandCoinsIcon,
  HistoryIcon,
  JapaneseYenIcon,
  ShieldCheckIcon,
  SlidersHorizontalIcon,
  StoreIcon,
  TagsIcon,
  TruckIcon,
  UsersIcon,
  type LucideIcon,
} from "lucide-react"

export type NavItem = {
  title: string
  description: string
  icon: LucideIcon
  href: string
}

export type NavGroup = {
  title: string
  items: NavItem[]
}

/**
 * 顶部导航与工作台卡片的单一数据源。
 * 新增功能时在此补 href，并按约定新增对应路由页面。
 */
export const NAV_GROUPS: NavGroup[] = [
  {
    title: "権限（ユーザー）管理",
    items: [
      {
        title: "ユーザー管理",
        description: "社内ユーザーの登録・編集・無効化を行います。",
        icon: UsersIcon,
        href: "/permissions/users",
      },
      {
        title: "ロール管理",
        description: "ロールと権限の割り当てを管理します。",
        icon: ShieldCheckIcon,
        href: "/permissions/roles",
      },
    ],
  },
  {
    title: "マスタ管理",
    items: [
      {
        title: "店舗管理",
        description: "請求対象の店舗マスタを管理します。",
        icon: StoreIcon,
        href: "/master/shops",
      },
      {
        title: "請求CD管理",
        description: "請求コードの定義と割り当てを管理します。",
        icon: TagsIcon,
        href: "/master/billing-codes",
      },
      {
        title: "単価管理",
        description: "業務ごとの単価マスタを管理します。",
        icon: JapaneseYenIcon,
        href: "/master/unit-prices",
      },
    ],
  },
  {
    title: "請求業務管理",
    items: [
      {
        title: "取込状態管理",
        description: "請求データの取込状況を確認します。",
        icon: FileInputIcon,
        href: "/billing/import-status",
      },
      {
        title: "請求承認管理",
        description: "請求内容の承認フローを管理します。",
        icon: BadgeCheckIcon,
        href: "/billing/approvals",
      },
      {
        title: "調整管理",
        description: "請求金額の調整を管理します。",
        icon: SlidersHorizontalIcon,
        href: "/billing/adjustments",
      },
      {
        title: "計上管理",
        description: "請求の計上処理を管理します。",
        icon: ClipboardListIcon,
        href: "/billing/postings",
      },
    ],
  },
  {
    title: "代引業務管理",
    items: [
      {
        title: "占位ページ 1",
        description: "代引業務管理の占位ページ（1）です。",
        icon: TruckIcon,
        href: "/cod/placeholder-1",
      },
      {
        title: "占位ページ 2",
        description: "代引業務管理の占位ページ（2）です。",
        icon: FileTextIcon,
        href: "/cod/placeholder-2",
      },
    ],
  },
  {
    title: "弁済業務管理",
    items: [
      {
        title: "占位ページ 1",
        description: "弁済業務管理の占位ページ（1）です。",
        icon: HandCoinsIcon,
        href: "/repayments/placeholder-1",
      },
      {
        title: "占位ページ 2",
        description: "弁済業務管理の占位ページ（2）です。",
        icon: FileTextIcon,
        href: "/repayments/placeholder-2",
      },
    ],
  },
  {
    title: "明細ダウンロード",
    items: [
      {
        title: "占位ページ 1",
        description: "明細ダウンロードの占位ページ（1）です。",
        icon: DownloadIcon,
        href: "/statements/placeholder-1",
      },
      {
        title: "占位ページ 2",
        description: "明細ダウンロードの占位ページ（2）です。",
        icon: HistoryIcon,
        href: "/statements/placeholder-2",
      },
    ],
  },
]
