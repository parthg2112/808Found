"use client"

import { motion, AnimatePresence } from "framer-motion"
import { X, Bell, AlertCircle, CheckCircle, Info } from "lucide-react"
import { Button } from "@/components/ui/button"

interface NotificationModalProps {
  isOpen: boolean
  onClose: () => void
}

interface Notification {
  id: string
  type: "info" | "success" | "warning"
  title: string
  message: string
  timestamp: string
}

export function NotificationModal({ isOpen, onClose }: NotificationModalProps) {
  const notifications: Notification[] = [
    {
      id: "1",
      type: "success",
      title: "Backtest Complete",
      message: "Your MA crossover backtest has finished successfully",
      timestamp: "2 min ago",
    },
    {
      id: "2",
      type: "info",
      title: "Data Updated",
      message: "Market data has been refreshed for all symbols",
      timestamp: "15 min ago",
    },
    {
      id: "3",
      type: "warning",
      title: "High Volatility Alert",
      message: "Unusual market movement detected in tech stocks",
      timestamp: "1 hour ago",
    },
  ]

  const getIcon = (type: string) => {
    switch (type) {
      case "success":
        return <CheckCircle className="h-5 w-5 text-green-400" />
      case "warning":
        return <AlertCircle className="h-5 w-5 text-yellow-400" />
      default:
        return <Info className="h-5 w-5 text-blue-400" />
    }
  }

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40"
          />

          {/* Modal */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: -20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: -20 }}
            transition={{ type: "spring", stiffness: 300, damping: 25 }}
            className="fixed top-20 right-4 md:right-6 w-full max-w-md max-h-96 bg-card border border-border rounded-lg shadow-xl z-50 overflow-hidden flex flex-col"
          >
            {/* Header */}
            <div className="flex items-center justify-between px-6 py-4 border-b border-border bg-secondary/30">
              <div className="flex items-center gap-2">
                <Bell className="h-5 w-5 text-blue-400" />
                <h2 className="text-lg font-semibold">Notifications</h2>
              </div>
              <Button variant="ghost" size="icon" onClick={onClose} className="h-8 w-8">
                <X className="h-4 w-4" />
              </Button>
            </div>

            {/* Notifications List */}
            <div className="flex-1 overflow-y-auto">
              {notifications.map((notif, idx) => (
                <motion.div
                  key={notif.id}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: idx * 0.05 }}
                  className="px-6 py-4 border-b border-border/50 hover:bg-secondary/50 transition-colors cursor-pointer"
                >
                  <div className="flex items-start gap-3">
                    {getIcon(notif.type)}
                    <div className="flex-1 min-w-0">
                      <h3 className="font-semibold text-sm">{notif.title}</h3>
                      <p className="text-sm text-muted-foreground mt-1">{notif.message}</p>
                      <p className="text-xs text-muted-foreground mt-2">{notif.timestamp}</p>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>

            {/* Footer */}
            <div className="px-6 py-3 border-t border-border bg-secondary/30">
              <Button variant="ghost" className="w-full text-xs h-8">
                View All Notifications
              </Button>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}
