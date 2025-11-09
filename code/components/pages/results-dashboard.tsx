"use client"

import { motion } from "framer-motion"
import { TrendingUp, TrendingDown } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts"

const metrics = [
  { label: "Total Return", value: "+24.5%", change: "+5.2%", positive: true },
  { label: "Win Rate", value: "65%", change: "+8.3%", positive: true },
  { label: "Profit Factor", value: "2.34", change: "+0.12", positive: true },
  { label: "Max Drawdown", value: "-8.2%", change: "-2.1%", positive: false },
  { label: "Avg Trade", value: "+$245", change: "+$32", positive: true },
  { label: "Sharpe Ratio", value: "1.85", change: "+0.24", positive: true },
]

const equityData = [
  { date: "Jan", equity: 10000, benchmark: 10000 },
  { date: "Feb", equity: 10850, benchmark: 10340 },
  { date: "Mar", equity: 11200, benchmark: 10680 },
  { date: "Apr", equity: 11800, benchmark: 11050 },
  { date: "May", equity: 12450, benchmark: 11350 },
  { date: "Jun", equity: 12800, benchmark: 11700 },
]

const tradeData = [
  { date: "2024-01-15", stock: "AAPL", entry: 182.5, exit: 185.25, profit: 2.75 },
  { date: "2024-01-18", stock: "TSLA", entry: 245.6, exit: 248.9, profit: 3.3 },
  { date: "2024-01-22", stock: "AAPL", entry: 186.2, exit: 183.5, profit: -2.7 },
  { date: "2024-01-25", stock: "TSLA", entry: 250.0, exit: 256.8, profit: 6.8 },
]

export function ResultsDashboard() {
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
    <div className="p-4 md:p-8 max-w-7xl mx-auto">
      <motion.div variants={containerVariants} initial="hidden" animate="visible">
        {/* Header */}
        <motion.div variants={itemVariants} className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Backtest Results</h1>
          <p className="text-muted-foreground">Detailed performance analysis and trade statistics</p>
        </motion.div>

        {/* Metrics Grid */}
        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          className="grid md:grid-cols-3 gap-4 mb-8"
        >
          {metrics.map((metric) => (
            <motion.div key={metric.label} variants={itemVariants}>
              <Card className="border-border hover:border-accent/50 transition-colors">
                <CardContent className="p-6">
                  <p className="text-sm text-muted-foreground mb-2">{metric.label}</p>
                  <div className="flex items-end justify-between">
                    <h3 className="text-2xl font-bold">{metric.value}</h3>
                    <div className="flex items-center gap-1">
                      {metric.positive ? (
                        <TrendingUp className="h-4 w-4 text-green-600" />
                      ) : (
                        <TrendingDown className="h-4 w-4 text-red-600" />
                      )}
                      <span className={`text-xs font-semibold ${metric.positive ? "text-green-600" : "text-red-600"}`}>
                        {metric.change}
                      </span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </motion.div>

        {/* Charts */}
        <motion.div variants={itemVariants} className="grid md:grid-cols-2 gap-6 mb-8">
          {/* Equity Curve */}
          <Card className="border-border">
            <CardHeader>
              <CardTitle>Equity Curve</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={equityData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                  <XAxis dataKey="date" stroke="var(--color-muted-foreground)" />
                  <YAxis stroke="var(--color-muted-foreground)" />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="equity" stroke="var(--color-accent)" name="Strategy" strokeWidth={2} />
                  <Line
                    type="monotone"
                    dataKey="benchmark"
                    stroke="var(--color-muted-foreground)"
                    name="Benchmark"
                    strokeWidth={2}
                    strokeDasharray="5 5"
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Trade Distribution */}
          <Card className="border-border">
            <CardHeader>
              <CardTitle>Trade Distribution</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={equityData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                  <XAxis dataKey="date" stroke="var(--color-muted-foreground)" />
                  <YAxis stroke="var(--color-muted-foreground)" />
                  <Tooltip />
                  <Bar dataKey="equity" fill="var(--color-accent)" radius={[8, 8, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </motion.div>

        {/* Trade Log */}
        <motion.div variants={itemVariants}>
          <Card className="border-border">
            <CardHeader>
              <CardTitle>Recent Trades</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-border">
                      <th className="text-left py-3 px-4 font-semibold text-muted-foreground">Date</th>
                      <th className="text-left py-3 px-4 font-semibold text-muted-foreground">Stock</th>
                      <th className="text-left py-3 px-4 font-semibold text-muted-foreground">Entry</th>
                      <th className="text-left py-3 px-4 font-semibold text-muted-foreground">Exit</th>
                      <th className="text-left py-3 px-4 font-semibold text-muted-foreground">Profit/Loss</th>
                    </tr>
                  </thead>
                  <tbody>
                    {tradeData.map((trade, idx) => (
                      <motion.tr
                        key={idx}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: idx * 0.05 }}
                        className="border-b border-border/50 hover:bg-secondary/50 transition-colors"
                      >
                        <td className="py-3 px-4">{trade.date}</td>
                        <td className="py-3 px-4 font-medium">{trade.stock}</td>
                        <td className="py-3 px-4">${trade.entry.toFixed(2)}</td>
                        <td className="py-3 px-4">${trade.exit.toFixed(2)}</td>
                        <td
                          className={`py-3 px-4 font-semibold ${trade.profit >= 0 ? "text-green-600" : "text-red-600"}`}
                        >
                          {trade.profit > 0 ? "+" : ""}
                          {trade.profit.toFixed(2)}%
                        </td>
                      </motion.tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </motion.div>
    </div>
  )
}
