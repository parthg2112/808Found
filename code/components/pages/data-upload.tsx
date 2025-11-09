"use client"

import type React from "react"

import { useState } from "react"
import { motion } from "framer-motion"
import { Upload, CheckCircle } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export function DataUpload() {
  const [dragActive, setDragActive] = useState(false)
  const [uploaded, setUploaded] = useState(false)
  const [fileName, setFileName] = useState("")

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true)
    } else if (e.type === "dragleave") {
      setDragActive(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    const files = e.dataTransfer.files
    if (files && files[0]) {
      setFileName(files[0].name)
      setUploaded(true)
    }
  }

  return (
    <div className="p-4 md:p-8 max-w-2xl mx-auto">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Upload Data</h1>
        <p className="text-muted-foreground">Import CSV files with historical price data</p>
      </motion.div>

      {/* Upload Zone */}
      <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} className="mb-8">
        <Card
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          className={`border-2 border-dashed transition-all cursor-pointer ${
            dragActive ? "border-accent bg-accent/5" : "border-border bg-secondary/50 hover:border-accent/50"
          }`}
        >
          <CardContent className="p-8">
            <motion.div
              animate={{
                y: dragActive ? -8 : 0,
              }}
              className="flex flex-col items-center justify-center"
            >
              <motion.div
                animate={{
                  scale: dragActive ? 1.1 : 1,
                  y: dragActive ? -4 : 0,
                }}
                className="mb-4"
              >
                <Upload className={`h-12 w-12 ${dragActive ? "text-accent" : "text-muted-foreground"}`} />
              </motion.div>
              <h3 className="text-lg font-semibold mb-1">Drop your CSV file here</h3>
              <p className="text-sm text-muted-foreground mb-4">or click to browse</p>
              <Button className="interactive">Choose File</Button>
            </motion.div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Upload Status */}
      {uploaded && (
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
          <Card className="border-green-500/30 bg-green-500/5">
            <CardContent className="p-6 flex items-center gap-4">
              <CheckCircle className="h-6 w-6 text-green-600 flex-shrink-0" />
              <div className="flex-1">
                <p className="font-semibold text-green-600">Upload successful!</p>
                <p className="text-sm text-muted-foreground">{fileName}</p>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* Preview Table */}
      {uploaded && (
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <Card className="border-border">
            <CardHeader>
              <CardTitle>Data Preview (First 5 rows)</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-border">
                      <th className="text-left py-2 px-4 font-semibold text-muted-foreground">Date</th>
                      <th className="text-left py-2 px-4 font-semibold text-muted-foreground">Open</th>
                      <th className="text-left py-2 px-4 font-semibold text-muted-foreground">High</th>
                      <th className="text-left py-2 px-4 font-semibold text-muted-foreground">Low</th>
                      <th className="text-left py-2 px-4 font-semibold text-muted-foreground">Close</th>
                      <th className="text-left py-2 px-4 font-semibold text-muted-foreground">Volume</th>
                    </tr>
                  </thead>
                  <tbody>
                    {[1, 2, 3, 4, 5].map((i) => (
                      <tr key={i} className="border-b border-border/50 hover:bg-secondary/50">
                        <td className="py-2 px-4">2024-01-{i * 5}</td>
                        <td className="py-2 px-4">182.50</td>
                        <td className="py-2 px-4">185.20</td>
                        <td className="py-2 px-4">181.80</td>
                        <td className="py-2 px-4">184.35</td>
                        <td className="py-2 px-4">52.2M</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}
    </div>
  )
}
