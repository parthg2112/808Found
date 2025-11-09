"use client"

import { motion, AnimatePresence } from "framer-motion"
import { X, Mail, LogOut, Settings, User } from "lucide-react"
import { Button } from "@/components/ui/button"

interface UserAccountModalProps {
  isOpen: boolean
  onClose: () => void
  onLogout: () => void
}

export function UserAccountModal({ isOpen, onClose, onLogout }: UserAccountModalProps) {
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
            className="fixed top-20 right-4 md:right-6 w-full max-w-sm bg-card border border-border rounded-lg shadow-xl z-50 overflow-hidden"
          >
            {/* Header */}
            <div className="flex items-center justify-between px-6 py-4 border-b border-border bg-secondary/30">
              <h2 className="text-lg font-semibold">Account</h2>
              <Button variant="ghost" size="icon" onClick={onClose} className="h-8 w-8">
                <X className="h-4 w-4" />
              </Button>
            </div>

            {/* User Info */}
            <div className="px-6 py-6 border-b border-border">
              <div className="flex items-center gap-4">
                <div className="h-12 w-12 rounded-full bg-blue-600 flex items-center justify-center">
                  <User className="h-6 w-6 text-white" />
                </div>
                <div>
                  <h3 className="font-semibold">John Trader</h3>
                  <p className="text-sm text-muted-foreground">john@example.com</p>
                </div>
              </div>
            </div>

            {/* Menu Items */}
            <div className="px-6 py-4 space-y-2">
              <motion.button
                whileHover={{ x: 4 }}
                className="w-full flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-secondary/50 transition-colors text-left text-sm"
              >
                <Mail className="h-4 w-4 text-muted-foreground" />
                <span>Email Preferences</span>
              </motion.button>

              <motion.button
                whileHover={{ x: 4 }}
                className="w-full flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-secondary/50 transition-colors text-left text-sm"
              >
                <Settings className="h-4 w-4 text-muted-foreground" />
                <span>Account Settings</span>
              </motion.button>
            </div>

            {/* Footer */}
            <div className="px-6 py-4 border-t border-border bg-secondary/20">
              <Button
                onClick={onLogout}
                variant="ghost"
                className="w-full gap-2 text-red-400 hover:bg-red-950/30 hover:text-red-300"
              >
                <LogOut className="h-4 w-4" />
                <span>Logout</span>
              </Button>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}
