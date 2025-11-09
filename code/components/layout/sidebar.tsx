"use client"

import { motion, AnimatePresence } from "framer-motion"
import { BarChart3, Upload, HelpCircle, LogOut, Zap, TrendingUp } from "lucide-react"
import { Button } from "@/components/ui/button"

type PageType = "home" | "config" | "backtest" | "results" | "upload" | "comparison" | "export"

interface SidebarProps {
  isOpen: boolean
  onNavigate: (page: PageType) => void
  currentPage: PageType
  onLogout: () => void
}

const menuItems = [
  { icon: BarChart3, label: "Dashboard", page: "home" as PageType },
  { icon: Zap, label: "New Backtest", page: "config" as PageType },
  { icon: TrendingUp, label: "View Results", page: "results" as PageType },
  { icon: Upload, label: "Upload Data", page: "upload" as PageType },
]

export function Sidebar({ isOpen, onNavigate, currentPage, onLogout }: SidebarProps) {
  return (
    <AnimatePresence>
      {isOpen && (
        <motion.aside
          initial={{ x: -250, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          exit={{ x: -250, opacity: 0 }}
          transition={{ duration: 0.3 }}
          className="w-64 bg-sidebar border-r border-sidebar-border flex flex-col hidden md:flex"
        >
          {/* Logo */}
          <div className="p-6 border-b border-sidebar-border">
            <div className="flex items-center gap-2">
              <div className="h-8 w-8 bg-blue-600 rounded-lg flex items-center justify-center">
                <Zap className="h-5 w-5 text-white" />
              </div>
              <span className="font-bold text-lg">808Found</span>
            </div>
          </div>

          {/* Menu Items */}
          <nav className="flex-1 px-4 py-6 space-y-2">
            {menuItems.map((item) => (
              <motion.div key={item.page} whileHover={{ x: 4 }} transition={{ duration: 0.2 }}>
                <Button
                  variant={currentPage === item.page ? "default" : "ghost"}
                  className="w-full justify-start gap-3 interactive"
                  onClick={() => onNavigate(item.page)}
                >
                  <item.icon className="h-4 w-4" />
                  <span>{item.label}</span>
                </Button>
              </motion.div>
            ))}
          </nav>

          {/* Footer */}
          <div className="p-4 border-t border-sidebar-border space-y-2">
            <Button
              variant="ghost"
              className="w-full justify-start gap-2 interactive text-muted-foreground hover:text-foreground"
            >
              <HelpCircle className="h-4 w-4" />
              <span>Help & Support</span>
            </Button>
            <Button
              onClick={onLogout}
              variant="ghost"
              className="w-full justify-start gap-2 interactive text-red-400 hover:bg-red-950/30 hover:text-red-300"
            >
              <LogOut className="h-4 w-4" />
              <span>Logout</span>
            </Button>
          </div>
        </motion.aside>
      )}
    </AnimatePresence>
  )
}
