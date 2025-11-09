"use client"

import { useState } from "react"
import { Landing } from "@/components/pages/landing"
import { SignInFlow } from "@/components/auth/sign-in-flow"
import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { DashboardHome } from "@/components/pages/dashboard-home"
import { ConfigurationPanel } from "@/components/pages/configuration-panel"
import { BacktestExecution } from "@/components/pages/backtest-execution"
import { ResultsDashboard } from "@/components/pages/results-dashboard"
import { DataUpload } from "@/components/pages/data-upload"

type PageType = "home" | "config" | "backtest" | "results" | "upload" | "comparison" | "export"
type AppState = "landing" | "signin" | "dashboard"

export default function Home() {
  const [appState, setAppState] = useState<AppState>("landing")
  const [currentPage, setCurrentPage] = useState<PageType>("home")

  if (appState === "landing") {
    return <Landing onGetStarted={() => setAppState("signin")} />
  }

  if (appState === "signin") {
    return <SignInFlow onSignInSuccess={() => setAppState("dashboard")} />
  }

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
    <DashboardLayout currentPage={currentPage} onNavigate={setCurrentPage} onLogout={() => setAppState("landing")}>
      {renderPage()}
    </DashboardLayout>
  )
}
