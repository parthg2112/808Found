"use client"

import { motion } from "framer-motion"
import { ArrowRight, BarChart3, Upload, Settings, type LucideIcon } from "lucide-react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { ShimmerBorderCard } from "@/components/ui/shimmer-border-card"
import { RainbowButton } from "@/components/ui/rainbow-button"

type PageType = "home" | "config" | "backtest" | "results" | "upload" | "comparison" | "export"

interface DashboardHomeProps {
  onNavigate: (page: PageType) => void
}

const features: { icon: LucideIcon; title: string; description: string; page: PageType }[] = [
  {
    icon: BarChart3,
    title: "Backtest Strategies",
    description: "Run MA crossover backtests with real market data and detailed performance analytics.",
    page: "config",
  },
  {
    icon: Upload,
    title: "Upload Data",
    description: "Import CSV files with historical price data and custom indicators.",
    page: "upload",
  },
  {
    icon: Settings,
    title: "Configuration",
    description: "Customize MA periods, stop-loss, take-profit, and position sizing.",
    page: "config",
  },
]

export function DashboardHome({ onNavigate }: DashboardHomeProps) {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
        delayChildren: 0.2,
      },
    },
  }

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: { y: 0, opacity: 1, transition: { duration: 0.4 } },
  }

  return (
    <div className="p-4 md:p-8 max-w-7xl mx-auto">
      {/* Hero Section */}
      <motion.div variants={containerVariants} initial="hidden" animate="visible" className="mb-12">
        <motion.h1 variants={itemVariants} className="text-4xl md:text-5xl font-bold tracking-tight mb-4">
          MA Crossover Backtester
        </motion.h1>
        <motion.p variants={itemVariants} className="text-lg text-muted-foreground mb-8">
          Test moving average crossover strategies with historical market data. Analyze performance metrics, equity
          curves, and trade statistics in real-time.
        </motion.p>
      </motion.div>

      {/* Feature Cards */}
      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        className="grid md:grid-cols-3 gap-6 mb-12"
      >
        {features.map((feature) => (
          <motion.div key={feature.title} variants={itemVariants}>
            <ShimmerBorderCard
              className="h-full"
              shimmerSize="0.1em"
              shimmerDuration="4s"
              onClick={() => onNavigate(feature.page)}
            >
              <Card
                className="h-full cursor-pointer border-0 transition-all duration-300 interactive group"
              >
                <CardHeader>
                  <div className="h-12 w-12 rounded-lg bg-accent/10 flex items-center justify-center mb-4 group-hover:bg-accent/20 transition-colors">
                    <feature.icon className="h-6 w-6 text-accent" />
                  </div>
                  <CardTitle>{feature.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-sm">{feature.description}</CardDescription>
                  <div className="mt-4 flex items-center gap-2 text-accent opacity-0 group-hover:opacity-100 transition-opacity">
                    <span className="text-sm font-medium">Get Started</span>
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </div>
                </CardContent>
              </Card>
            </ShimmerBorderCard>
          </motion.div>
        ))}
      </motion.div>

      {/* CTA Section */}
      <motion.div
        variants={itemVariants}
        initial="hidden"
        animate="visible"
        className="bg-secondary/50 border border-border rounded-lg p-8 md:p-12 text-center"
      >
        <h2 className="text-2xl font-semibold mb-4">Ready to backtest your strategy?</h2>
        <p className="text-muted-foreground mb-6">
          Start by configuring your MA crossover parameters and select the stocks you want to analyze.
        </p>
        <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
          <RainbowButton size="lg" onClick={() => onNavigate("config")} className="interactive">
            Start Backtesting <ArrowRight className="ml-2 h-4 w-4" />
          </RainbowButton>
        </motion.div>
      </motion.div>
    </div>
  )
}