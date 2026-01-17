"use client"

import { useState } from "react"
import { signOut } from "next-auth/react"
import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { DashboardHome } from "@/components/pages/dashboard-home"
import { ConfigurationPanel } from "@/components/pages/configuration-panel"
import { BacktestExecution } from "@/components/pages/backtest-execution"
import { ResultsDashboard } from "@/components/pages/results-dashboard"
import { DataUpload } from "@/components/pages/data-upload"

type PageType = "home" | "config" | "backtest" | "results" | "upload" | "comparison" | "export"

export default function DashboardApp() {
  const [currentPage, setCurrentPage] = useState<PageType>("home")

  const renderPage = () => {
    switch (currentPage) {
      case "config":
        return <ConfigurationPanel onNext={() => setCurrentPage("backtest")} />
      case "backtest":
        return <BacktestExecution onNext={() => setCurrentPage("results")} />
      case "results":
        return <ResultsDashboard />
      case "upload":
        return <DataUpload />
      default:
        return <DashboardHome onNavigate={setCurrentPage} />
    }
  }

  return (
    <DashboardLayout 
      currentPage={currentPage} 
      onNavigate={setCurrentPage} 
      onLogout={() => signOut({ callbackUrl: "/" })}
    >
      {renderPage()}
    </DashboardLayout>
  )
}
