"use client"

import { useState, useEffect } from "react"
import { motion } from "framer-motion"
import { Play, Pause, RotateCcw } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"

interface BacktestExecutionProps {
  onNext: () => void
}

export function BacktestExecution({ onNext }: BacktestExecutionProps) {
  const [progress, setProgress] = useState(0)
  const [isRunning, setIsRunning] = useState(false)
  const [currentStock, setCurrentStock] = useState("AAPL")

  useEffect(() => {
    if (!isRunning) return

    const interval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 100) {
          setIsRunning(false)
          setTimeout(() => onNext(), 1500)
          return 100
        }
        return prev + 2
      })
    }, 100)

    return () => clearInterval(interval)
  }, [isRunning, onNext])

  const stocks = ["AAPL", "TSLA"]
  const currentIndex = stocks.indexOf(currentStock)
  const totalStocks = stocks.length

  return (
    <div className="p-4 md:p-8 max-w-2xl mx-auto h-full flex flex-col items-center justify-center">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="text-center mb-12">
        <h1 className="text-3xl font-bold mb-2">Running Backtest</h1>
        <p className="text-muted-foreground">Processing historical data and generating results...</p>
      </motion.div>

      <Card className="w-full border-border mb-8">
        <CardContent className="p-8">
          {/* Progress Visualization */}
          <motion.div initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} className="mb-8">
            <div className="h-32 bg-gradient-to-b from-accent/20 to-transparent rounded-lg flex items-center justify-center mb-6 relative overflow-hidden">
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 2, repeat: Number.POSITIVE_INFINITY, ease: "linear" }}
                className="w-16 h-16 border-4 border-accent/30 border-t-accent rounded-full"
              />
            </div>

            {/* Status Text */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.2 }}
              className="text-center"
            >
              <p className="text-lg font-semibold mb-2">
                Processing <span className="text-accent">{currentStock}</span>
              </p>
              <motion.p className="text-sm text-muted-foreground">
                {Math.round(progress)}% complete
                <motion.span
                  animate={{ opacity: [0.5, 1, 0.5] }}
                  transition={{ duration: 1, repeat: Number.POSITIVE_INFINITY }}
                >
                  ...
                </motion.span>
              </motion.p>
            </motion.div>
          </motion.div>

          {/* Progress Bar */}
          <div className="mb-6">
            <div className="w-full h-2 bg-secondary rounded-full overflow-hidden">
              <motion.div
                className="h-full bg-gradient-to-r from-accent to-accent/70"
                initial={{ width: 0 }}
                animate={{ width: `${progress}%` }}
                transition={{ duration: 0.3 }}
              />
            </div>
            <div className="flex justify-between mt-2 text-xs text-muted-foreground">
              <span>
                Stock {currentIndex + 1} of {totalStocks}
              </span>
              <span>{Math.round(progress)}%</span>
            </div>
          </div>

          {/* Stock Progress */}
          <div className="space-y-2">
            {stocks.map((stock, idx) => (
              <motion.div
                key={stock}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: idx * 0.1 }}
                className="flex items-center gap-3 text-sm"
              >
                <div
                  className={`w-2 h-2 rounded-full ${
                    idx < currentIndex ? "bg-green-500" : idx === currentIndex ? "bg-accent" : "bg-muted"
                  }`}
                />
                <span className={idx <= currentIndex ? "text-foreground" : "text-muted-foreground"}>{stock}</span>
              </motion.div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Controls */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="flex gap-4 w-full"
      >
        <Button
          variant="outline"
          className="flex-1 interactive bg-transparent"
          onClick={() => setIsRunning(!isRunning)}
        >
          {isRunning ? (
            <>
              <Pause className="h-4 w-4 mr-2" />
              Pause
            </>
          ) : (
            <>
              <Play className="h-4 w-4 mr-2" />
              {progress === 0 ? "Start" : "Resume"}
            </>
          )}
        </Button>
        <Button
          variant="outline"
          className="flex-1 interactive bg-transparent"
          onClick={() => {
            setProgress(0)
            setIsRunning(false)
            setCurrentStock("AAPL")
          }}
        >
          <RotateCcw className="h-4 w-4 mr-2" />
          Reset
        </Button>
      </motion.div>

      {/* Auto-start hint */}
      <motion.p
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1 }}
        className="text-xs text-muted-foreground mt-6"
      >
        Click "Start" to begin the backtest
      </motion.p>
    </div>
  )
}
