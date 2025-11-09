"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import { X } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"

interface ConfigurationPanelProps {
  onNext: () => void
}

export function ConfigurationPanel({ onNext }: ConfigurationPanelProps) {
  const [shortMA, setShortMA] = useState(20)
  const [longMA, setLongMA] = useState(50)
  const [stopLoss, setStopLoss] = useState(2)
  const [takeProfit, setTakeProfit] = useState(5)
  const [positionSize, setPositionSize] = useState(1000)
  const [selectedStocks, setSelectedStocks] = useState<string[]>(["AAPL", "TSLA"])
  const [stockInput, setStockInput] = useState("")

  const allStocks = ["AAPL", "MSFT", "GOOGL", "TSLA", "AMZN", "NFLX", "META", "NVIDIA"]

  const addStock = (stock: string) => {
    if (!selectedStocks.includes(stock)) {
      setSelectedStocks([...selectedStocks, stock])
    }
  }

  const removeStock = (stock: string) => {
    setSelectedStocks(selectedStocks.filter((s) => s !== stock))
  }

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.08,
        delayChildren: 0.1,
      },
    },
  }

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: { y: 0, opacity: 1, transition: { duration: 0.4 } },
  }

  return (
    <div className="p-4 md:p-8 max-w-4xl mx-auto">
      <motion.div variants={containerVariants} initial="hidden" animate="visible">
        <motion.div variants={itemVariants} className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Configure Strategy</h1>
          <p className="text-muted-foreground">Set up your MA crossover parameters and select stocks to backtest</p>
        </motion.div>

        {/* Strategy Config */}
        <motion.div variants={itemVariants}>
          <Card className="mb-6 border-border">
            <CardHeader>
              <CardTitle>Moving Average Settings</CardTitle>
              <CardDescription>Configure short and long MA periods</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <label className="text-sm font-medium mb-2 block">Short MA Period</label>
                  <div className="flex items-center gap-4">
                    <Input
                      type="number"
                      value={shortMA}
                      onChange={(e) => setShortMA(Number(e.target.value))}
                      className="interactive"
                      min={5}
                      max={50}
                    />
                    <span className="text-sm text-muted-foreground w-12">{shortMA}</span>
                  </div>
                  <input
                    type="range"
                    min={5}
                    max={50}
                    value={shortMA}
                    onChange={(e) => setShortMA(Number(e.target.value))}
                    className="w-full mt-2"
                  />
                </div>

                <div>
                  <label className="text-sm font-medium mb-2 block">Long MA Period</label>
                  <div className="flex items-center gap-4">
                    <Input
                      type="number"
                      value={longMA}
                      onChange={(e) => setLongMA(Number(e.target.value))}
                      className="interactive"
                      min={20}
                      max={200}
                    />
                    <span className="text-sm text-muted-foreground w-12">{longMA}</span>
                  </div>
                  <input
                    type="range"
                    min={20}
                    max={200}
                    value={longMA}
                    onChange={(e) => setLongMA(Number(e.target.value))}
                    className="w-full mt-2"
                  />
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Risk Management */}
        <motion.div variants={itemVariants}>
          <Card className="mb-6 border-border">
            <CardHeader>
              <CardTitle>Risk Management</CardTitle>
              <CardDescription>Set stop-loss and take-profit levels</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <label className="text-sm font-medium mb-2 block">Stop Loss (%)</label>
                  <div className="flex items-center gap-4">
                    <Input
                      type="number"
                      value={stopLoss}
                      onChange={(e) => setStopLoss(Number(e.target.value))}
                      className="interactive"
                      step={0.1}
                      min={0.1}
                      max={10}
                    />
                    <span className="text-sm text-destructive font-semibold">{stopLoss}%</span>
                  </div>
                </div>

                <div>
                  <label className="text-sm font-medium mb-2 block">Take Profit (%)</label>
                  <div className="flex items-center gap-4">
                    <Input
                      type="number"
                      value={takeProfit}
                      onChange={(e) => setTakeProfit(Number(e.target.value))}
                      className="interactive"
                      step={0.1}
                      min={0.1}
                      max={20}
                    />
                    <span className="text-sm text-green-600 font-semibold">{takeProfit}%</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Position Sizing */}
        <motion.div variants={itemVariants}>
          <Card className="mb-6 border-border">
            <CardHeader>
              <CardTitle>Position Sizing</CardTitle>
              <CardDescription>Set position size per trade</CardDescription>
            </CardHeader>
            <CardContent>
              <div>
                <label className="text-sm font-medium mb-2 block">Position Size ($)</label>
                <Input
                  type="number"
                  value={positionSize}
                  onChange={(e) => setPositionSize(Number(e.target.value))}
                  className="interactive"
                  step={100}
                  min={100}
                  max={100000}
                />
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Stock Selection */}
        <motion.div variants={itemVariants}>
          <Card className="border-border">
            <CardHeader>
              <CardTitle>Select Stocks</CardTitle>
              <CardDescription>Choose stocks to backtest the strategy</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex gap-2 flex-wrap">
                {allStocks.map((stock) => (
                  <motion.button
                    key={stock}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => (selectedStocks.includes(stock) ? removeStock(stock) : addStock(stock))}
                    className={`px-4 py-2 rounded-lg font-medium text-sm transition-all interactive ${
                      selectedStocks.includes(stock)
                        ? "bg-accent text-accent-foreground"
                        : "bg-secondary text-foreground border border-border hover:border-accent"
                    }`}
                  >
                    {stock}
                  </motion.button>
                ))}
              </div>

              {selectedStocks.length > 0 && (
                <div className="mt-4 p-4 bg-secondary/50 rounded-lg">
                  <p className="text-sm font-medium mb-2">Selected: {selectedStocks.length} stocks</p>
                  <div className="flex gap-2 flex-wrap">
                    {selectedStocks.map((stock) => (
                      <motion.div
                        key={stock}
                        initial={{ scale: 0.9, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        className="inline-flex items-center gap-2 bg-background px-3 py-1 rounded-full text-sm border border-border"
                      >
                        {stock}
                        <button onClick={() => removeStock(stock)} className="hover:text-destructive">
                          <X className="h-3 w-3" />
                        </button>
                      </motion.div>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </motion.div>

        {/* Actions */}
        <motion.div variants={itemVariants} className="flex gap-4 mt-8">
          <Button variant="outline" className="interactive bg-transparent">
            Save Configuration
          </Button>
          <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }} className="flex-1">
            <Button className="w-full interactive" onClick={onNext} disabled={selectedStocks.length === 0}>
              Next: Run Backtest
            </Button>
          </motion.div>
        </motion.div>
      </motion.div>
    </div>
  )
}
