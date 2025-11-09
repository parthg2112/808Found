"use client"

import type React from "react"
import { useState } from "react"
import { motion } from "framer-motion"
import { Menu, X, Bell, User } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Sidebar } from "@/components/layout/sidebar"
import { NotificationModal } from "@/components/modals/notification-modal"
import { UserAccountModal } from "@/components/modals/user-account-modal"

type PageType = "home" | "config" | "backtest" | "results" | "upload" | "comparison" | "export"

interface DashboardLayoutProps {
  currentPage: PageType
  onNavigate: (page: PageType) => void
  onLogout: () => void
  children: React.ReactNode
}

export function DashboardLayout({ currentPage, onNavigate, onLogout, children }: DashboardLayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [notificationOpen, setNotificationOpen] = useState(false)
  const [userMenuOpen, setUserMenuOpen] = useState(false)

  return (
    <div className="dark flex h-screen bg-background text-foreground">
      {/* Sidebar */}
      <Sidebar isOpen={sidebarOpen} onNavigate={onNavigate} currentPage={currentPage} onLogout={onLogout} />

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top Bar */}
        <motion.header
          className="border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 sticky top-0 z-40"
          initial={{ y: -20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.3 }}
        >
          <div className="flex items-center justify-between px-4 md:px-6 py-3 md:py-4">
            <div className="flex items-center gap-4">
              <Button variant="ghost" size="icon" onClick={() => setSidebarOpen(!sidebarOpen)} className="md:hidden">
                {sidebarOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
              </Button>
              <h1 className="text-lg md:text-xl font-semibold">808Found Backtester</h1>
            </div>

            <div className="flex items-center gap-2 md:gap-4">
              <Button
                variant="ghost"
                size="icon"
                className="rounded-full interactive"
                onClick={() => setNotificationOpen(true)}
              >
                <Bell className="h-5 w-5" />
              </Button>
              <Button
                variant="ghost"
                size="icon"
                className="rounded-full interactive"
                onClick={() => setUserMenuOpen(true)}
              >
                <User className="h-5 w-5" />
              </Button>
            </div>
          </div>
        </motion.header>

        {/* Page Content */}
        <motion.main
          className="flex-1 overflow-auto"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          {children}
        </motion.main>
      </div>

      {/* Modals */}
      <NotificationModal isOpen={notificationOpen} onClose={() => setNotificationOpen(false)} />
      <UserAccountModal
        isOpen={userMenuOpen}
        onClose={() => setUserMenuOpen(false)}
        onLogout={() => {
          setUserMenuOpen(false)
          onLogout()
        }}
      />
    </div>
  )
}
