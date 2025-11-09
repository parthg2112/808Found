"use client"

import { motion } from "framer-motion"
import { WebGLShader } from "@/components/webgl/web-gl-shader"
import { Button } from "@/components/ui/button"
import { Zap, TrendingUp, BarChart3, Rocket } from "lucide-react"

interface LandingProps {
  onGetStarted: () => void
}

export function Landing({ onGetStarted }: LandingProps) {
  return (
    <div className="relative w-full h-screen overflow-hidden bg-black">
      {/* WebGL Background */}
      <WebGLShader />

      {/* Content Overlay */}
      <div className="absolute inset-0 flex flex-col items-center justify-center z-10">
        {/* Gradient Overlay for better text visibility */}
        <div className="absolute inset-0 bg-gradient-to-b from-black/40 via-black/30 to-black/60" />

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="relative z-20 text-center max-w-3xl mx-auto px-4"
        >
          {/* Logo/Brand */}
          <motion.div
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: 0.6 }}
            className="mb-8 inline-flex items-center gap-3 px-4 py-2 rounded-full border border-blue-500/30 bg-blue-500/10 backdrop-blur-sm"
          >
            <Rocket className="h-5 w-5 text-blue-400" />
            <span className="text-blue-300 font-semibold">Introducing 808Found</span>
          </motion.div>

          {/* Main Heading */}
          <motion.h1
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.3 }}
            className="text-5xl md:text-7xl font-bold text-white mb-6 tracking-tight"
          >
            Advanced MA Crossover
            <span className="bg-gradient-to-r from-blue-400 via-cyan-300 to-blue-300 bg-clip-text text-transparent">
              {" "}
              Backtester
            </span>
          </motion.h1>

          {/* Subheading */}
          <motion.p
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.4 }}
            className="text-lg md:text-xl text-gray-300 mb-12 max-w-2xl mx-auto leading-relaxed"
          >
            Professional-grade algorithmic trading platform for testing moving average crossover strategies with
            real-time market data analysis
          </motion.p>

          {/* Feature Pills */}
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.5 }}
            className="flex flex-wrap justify-center gap-4 mb-12"
          >
            {[
              { icon: Zap, label: "Fast Backtest Engine" },
              { icon: TrendingUp, label: "Real-time Analytics" },
              { icon: BarChart3, label: "Advanced Charts" },
            ].map((feature, idx) => (
              <div
                key={idx}
                className="flex items-center gap-2 px-4 py-2 rounded-lg bg-white/5 border border-white/10 backdrop-blur-sm hover:bg-white/10 transition-colors"
              >
                <feature.icon className="h-4 w-4 text-blue-400" />
                <span className="text-sm text-gray-200">{feature.label}</span>
              </div>
            ))}
          </motion.div>

          {/* CTA Button */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.6, delay: 0.6 }}
          >
            <Button
              onClick={onGetStarted}
              className="px-8 py-6 text-lg font-semibold bg-blue-600 hover:bg-blue-700 text-white rounded-lg shadow-lg hover:shadow-blue-500/50 transition-all interactive"
            >
              Get Started
              <motion.div animate={{ x: [0, 4, 0] }} transition={{ duration: 1.5, repeat: Number.POSITIVE_INFINITY }}>
                →
              </motion.div>
            </Button>
          </motion.div>
        </motion.div>
      </div>
    </div>
  )
}
