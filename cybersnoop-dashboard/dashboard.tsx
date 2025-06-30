"use client"

import { useState, useEffect } from "react"
import {
  Play,
  Square,
  Settings,
  Filter,
  Download,
  Shield,
  AlertTriangle,
  Activity,
  Network,
  ChevronDown,
  Search,
  Database,
  Cpu,
  HardDrive,
  Lock,
  X,
  Plus,
  BarChart3,
  FileText,
  Save,
  FolderOpen,
  HelpCircle,
  Maximize2,
  Minimize2,
  Zap,
  Bug,
  Skull,
  Target,
} from "lucide-react"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Progress } from "@/components/ui/progress"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
} from "@/components/ui/dropdown-menu"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"

// Mock data
const mockPackets = [
  {
    id: 1,
    time: "14:23:45.123",
    sourceIP: "192.168.1.100",
    destIP: "8.8.8.8",
    protocol: "HTTPS",
    port: 443,
    length: 1420,
    info: "TLS Application Data",
    threatLevel: "safe",
  },
  {
    id: 2,
    time: "14:23:45.124",
    sourceIP: "10.0.0.15",
    destIP: "192.168.1.1",
    protocol: "SSH",
    port: 22,
    length: 96,
    info: "SSH Protocol",
    threatLevel: "suspicious",
  },
  {
    id: 3,
    time: "14:23:45.125",
    sourceIP: "172.16.0.50",
    destIP: "192.168.1.100",
    protocol: "TCP",
    port: 80,
    length: 1500,
    info: "HTTP GET Request",
    threatLevel: "threat",
  },
  {
    id: 4,
    time: "14:23:45.126",
    sourceIP: "192.168.1.200",
    destIP: "1.1.1.1",
    protocol: "DNS",
    port: 53,
    length: 64,
    info: "Standard Query",
    threatLevel: "safe",
  },
  {
    id: 5,
    time: "14:23:45.127",
    sourceIP: "203.0.113.1",
    destIP: "192.168.1.100",
    protocol: "TCP",
    port: 3389,
    length: 128,
    info: "RDP Connection Attempt",
    threatLevel: "threat",
  },
]

const mockThreats = [
  {
    id: 1,
    type: "Port Scan",
    severity: "high",
    source: "203.0.113.1",
    time: "14:23:45",
    description: "Multiple port scan detected from external IP",
  },
  {
    id: 2,
    type: "Brute Force",
    severity: "critical",
    source: "172.16.0.50",
    time: "14:23:40",
    description: "SSH brute force attack detected",
  },
  {
    id: 3,
    type: "Suspicious Traffic",
    severity: "medium",
    source: "10.0.0.15",
    time: "14:23:30",
    description: "Unusual data patterns detected",
  },
]

const getThreatIcon = (type: string) => {
  switch (type) {
    case "Port Scan":
      return <Target className="h-4 w-4" />
    case "Brute Force":
      return <Skull className="h-4 w-4" />
    case "DDoS":
      return <Zap className="h-4 w-4" />
    case "Malware":
      return <Bug className="h-4 w-4" />
    default:
      return <AlertTriangle className="h-4 w-4" />
  }
}

const getThreatColor = (severity: string) => {
  switch (severity) {
    case "critical":
      return "text-red-500 bg-red-500/10"
    case "high":
      return "text-orange-500 bg-orange-500/10"
    case "medium":
      return "text-yellow-500 bg-yellow-500/10"
    case "low":
      return "text-blue-500 bg-blue-500/10"
    default:
      return "text-gray-500 bg-gray-500/10"
  }
}

const getPacketColor = (threatLevel: string) => {
  switch (threatLevel) {
    case "threat":
      return "bg-red-500/10 text-red-400 border-red-500/20"
    case "suspicious":
      return "bg-yellow-500/10 text-yellow-400 border-yellow-500/20"
    case "safe":
      return "bg-green-500/10 text-green-400 border-green-500/20"
    default:
      return "bg-gray-500/10 text-gray-400 border-gray-500/20"
  }
}

export default function CyberSnoopDashboard() {
  const [isCapturing, setIsCapturing] = useState(false)
  const [selectedInterface, setSelectedInterface] = useState("eth0")
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
  const [packetsPerSec, setPacketsPerSec] = useState(1247)
  const [threatsPerSec, setThreatsPerSec] = useState(3)
  const [totalPackets, setTotalPackets] = useState(45672)
  const [filterText, setFilterText] = useState("")

  // Simulate real-time updates
  useEffect(() => {
    const interval = setInterval(() => {
      if (isCapturing) {
        setPacketsPerSec((prev) => prev + Math.floor(Math.random() * 100) - 50)
        setThreatsPerSec((prev) => Math.max(0, prev + Math.floor(Math.random() * 3) - 1))
        setTotalPackets((prev) => prev + Math.floor(Math.random() * 10))
      }
    }, 1000)

    return () => clearInterval(interval)
  }, [isCapturing])

  return (
    <TooltipProvider>
      <div className="h-screen bg-[#2b2b2b] text-gray-100 flex flex-col overflow-hidden">
        {/* Top Menu Bar */}
        <div className="bg-[#1e1e1e] border-b border-gray-700 px-4 py-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-6">
              <div className="flex items-center space-x-2">
                <Shield className="h-6 w-6 text-blue-400" />
                <span className="text-lg font-semibold text-white">CyberSnoop</span>
              </div>

              <div className="flex items-center space-x-4">
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" size="sm" className="text-gray-300 hover:text-white">
                      File <ChevronDown className="ml-1 h-3 w-3" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent className="bg-[#3c3c3c] border-gray-600">
                    <DropdownMenuItem className="text-gray-300 hover:text-white hover:bg-gray-700">
                      <FolderOpen className="mr-2 h-4 w-4" />
                      Open
                    </DropdownMenuItem>
                    <DropdownMenuItem className="text-gray-300 hover:text-white hover:bg-gray-700">
                      <Save className="mr-2 h-4 w-4" />
                      Save
                    </DropdownMenuItem>
                    <DropdownMenuItem className="text-gray-300 hover:text-white hover:bg-gray-700">
                      <Download className="mr-2 h-4 w-4" />
                      Export Logs
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>

                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" size="sm" className="text-gray-300 hover:text-white">
                      Capture <ChevronDown className="ml-1 h-3 w-3" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent className="bg-[#3c3c3c] border-gray-600">
                    <DropdownMenuItem className="text-gray-300 hover:text-white hover:bg-gray-700">
                      <Play className="mr-2 h-4 w-4" />
                      Start Capture
                    </DropdownMenuItem>
                    <DropdownMenuItem className="text-gray-300 hover:text-white hover:bg-gray-700">
                      <Square className="mr-2 h-4 w-4" />
                      Stop Capture
                    </DropdownMenuItem>
                    <DropdownMenuSeparator className="bg-gray-600" />
                    <DropdownMenuItem className="text-gray-300 hover:text-white hover:bg-gray-700">
                      <Network className="mr-2 h-4 w-4" />
                      Interface Selection
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>

                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" size="sm" className="text-gray-300 hover:text-white">
                      View <ChevronDown className="ml-1 h-3 w-3" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent className="bg-[#3c3c3c] border-gray-600">
                    <DropdownMenuItem className="text-gray-300 hover:text-white hover:bg-gray-700">
                      <Filter className="mr-2 h-4 w-4" />
                      Filters
                    </DropdownMenuItem>
                    <DropdownMenuItem className="text-gray-300 hover:text-white hover:bg-gray-700">
                      <BarChart3 className="mr-2 h-4 w-4" />
                      Columns
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>

                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" size="sm" className="text-gray-300 hover:text-white">
                      Tools <ChevronDown className="ml-1 h-3 w-3" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent className="bg-[#3c3c3c] border-gray-600">
                    <DropdownMenuItem className="text-gray-300 hover:text-white hover:bg-gray-700">
                      <Settings className="mr-2 h-4 w-4" />
                      Settings
                    </DropdownMenuItem>
                    <DropdownMenuItem className="text-gray-300 hover:text-white hover:bg-gray-700">
                      <Lock className="mr-2 h-4 w-4" />
                      Blacklist Management
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>

                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" size="sm" className="text-gray-300 hover:text-white">
                      Help <ChevronDown className="ml-1 h-3 w-3" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent className="bg-[#3c3c3c] border-gray-600">
                    <DropdownMenuItem className="text-gray-300 hover:text-white hover:bg-gray-700">
                      <HelpCircle className="mr-2 h-4 w-4" />
                      Documentation
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <div className="flex items-center space-x-1">
                  <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                  <span className="text-xs text-gray-400">Admin</span>
                </div>
                <Separator orientation="vertical" className="h-4 bg-gray-600" />
                <div className="flex items-center space-x-1">
                  <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                  <span className="text-xs text-gray-400">Npcap Ready</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Control Panel */}
        <div className="bg-[#3c3c3c] border-b border-gray-700 px-4 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Select value={selectedInterface} onValueChange={setSelectedInterface}>
                <SelectTrigger className="w-40 bg-[#2b2b2b] border-gray-600 text-gray-300">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-[#2b2b2b] border-gray-600">
                  <SelectItem value="eth0">Ethernet (eth0)</SelectItem>
                  <SelectItem value="wlan0">WiFi (wlan0)</SelectItem>
                  <SelectItem value="lo">Loopback (lo)</SelectItem>
                </SelectContent>
              </Select>

              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    onClick={() => setIsCapturing(!isCapturing)}
                    className={`${isCapturing ? "bg-red-600 hover:bg-red-700" : "bg-green-600 hover:bg-green-700"} text-white`}
                  >
                    {isCapturing ? <Square className="h-4 w-4 mr-2" /> : <Play className="h-4 w-4 mr-2" />}
                    {isCapturing ? "Stop" : "Start"}
                  </Button>
                </TooltipTrigger>
                <TooltipContent>{isCapturing ? "Stop packet capture" : "Start packet capture"}</TooltipContent>
              </Tooltip>

              <div className="flex items-center space-x-2">
                <div
                  className={`w-3 h-3 rounded-full ${isCapturing ? "bg-green-500 animate-pulse" : "bg-gray-500"}`}
                ></div>
                <span className="text-sm text-gray-400">{isCapturing ? "Live Capture" : "Stopped"}</span>
              </div>

              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  placeholder="Quick filter..."
                  value={filterText}
                  onChange={(e) => setFilterText(e.target.value)}
                  className="pl-10 w-64 bg-[#2b2b2b] border-gray-600 text-gray-300 placeholder-gray-500"
                />
              </div>
            </div>

            <div className="flex items-center space-x-6">
              <div className="flex items-center space-x-4 text-sm">
                <div className="flex items-center space-x-2">
                  <Activity className="h-4 w-4 text-blue-400" />
                  <span className="text-gray-400">Packets/sec:</span>
                  <span className="text-white font-mono">{packetsPerSec.toLocaleString()}</span>
                </div>
                <div className="flex items-center space-x-2">
                  <AlertTriangle className="h-4 w-4 text-red-400" />
                  <span className="text-gray-400">Threats/sec:</span>
                  <span className="text-white font-mono">{threatsPerSec}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Main Content Area */}
        <div className="flex-1 flex overflow-hidden">
          {/* Main Panel */}
          <div className="flex-1 flex flex-col">
            <Tabs defaultValue="live" className="flex-1 flex flex-col">
              <TabsList className="bg-[#3c3c3c] border-b border-gray-700 rounded-none justify-start px-4">
                <TabsTrigger value="live" className="data-[state=active]:bg-[#0078d4] data-[state=active]:text-white">
                  Live Capture
                </TabsTrigger>
                <TabsTrigger
                  value="threats"
                  className="data-[state=active]:bg-[#0078d4] data-[state=active]:text-white"
                >
                  Threat Analysis
                </TabsTrigger>
                <TabsTrigger
                  value="historical"
                  className="data-[state=active]:bg-[#0078d4] data-[state=active]:text-white"
                >
                  Historical Data
                </TabsTrigger>
              </TabsList>

              <TabsContent value="live" className="flex-1 flex flex-col m-0">
                {/* Packet Capture Table */}
                <div className="flex-1 bg-[#2b2b2b] border-b border-gray-700">
                  <div className="h-full overflow-auto">
                    <Table>
                      <TableHeader className="sticky top-0 bg-[#3c3c3c] border-b border-gray-700">
                        <TableRow className="hover:bg-transparent border-gray-700">
                          <TableHead className="text-gray-300 font-semibold">Time</TableHead>
                          <TableHead className="text-gray-300 font-semibold">Source IP</TableHead>
                          <TableHead className="text-gray-300 font-semibold">Dest IP</TableHead>
                          <TableHead className="text-gray-300 font-semibold">Protocol</TableHead>
                          <TableHead className="text-gray-300 font-semibold">Port</TableHead>
                          <TableHead className="text-gray-300 font-semibold">Length</TableHead>
                          <TableHead className="text-gray-300 font-semibold">Info</TableHead>
                          <TableHead className="text-gray-300 font-semibold">Threat Level</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {mockPackets.map((packet) => (
                          <TableRow
                            key={packet.id}
                            className={`hover:bg-gray-700/50 border-gray-700 ${getPacketColor(packet.threatLevel)}`}
                          >
                            <TableCell className="font-mono text-xs">{packet.time}</TableCell>
                            <TableCell className="font-mono text-xs">{packet.sourceIP}</TableCell>
                            <TableCell className="font-mono text-xs">{packet.destIP}</TableCell>
                            <TableCell>
                              <Badge variant="outline" className="text-xs">
                                {packet.protocol}
                              </Badge>
                            </TableCell>
                            <TableCell className="font-mono text-xs">{packet.port}</TableCell>
                            <TableCell className="font-mono text-xs">{packet.length}</TableCell>
                            <TableCell className="text-xs">{packet.info}</TableCell>
                            <TableCell>
                              <Badge variant="outline" className={`text-xs ${getPacketColor(packet.threatLevel)}`}>
                                {packet.threatLevel}
                              </Badge>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </div>
                </div>

                {/* Threat Detection Panel */}
                <div className="h-64 bg-[#2b2b2b] border-b border-gray-700">
                  <div className="p-4">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg font-semibold text-white flex items-center">
                        <AlertTriangle className="h-5 w-5 mr-2 text-red-400" />
                        Threat Detection
                      </h3>
                      <Button size="sm" variant="outline" className="border-gray-600 text-gray-300 hover:text-white">
                        <Download className="h-4 w-4 mr-2" />
                        Export Threats
                      </Button>
                    </div>
                    <div className="space-y-2">
                      {mockThreats.map((threat) => (
                        <div key={threat.id} className={`p-3 rounded-lg border ${getThreatColor(threat.severity)}`}>
                          <div className="flex items-center justify-between">
                            <div className="flex items-center space-x-3">
                              {getThreatIcon(threat.type)}
                              <div>
                                <div className="flex items-center space-x-2">
                                  <span className="font-semibold">{threat.type}</span>
                                  <Badge variant="outline" className={getThreatColor(threat.severity)}>
                                    {threat.severity}
                                  </Badge>
                                </div>
                                <p className="text-sm text-gray-400 mt-1">{threat.description}</p>
                                <p className="text-xs text-gray-500 mt-1">
                                  Source: {threat.source} • {threat.time}
                                </p>
                              </div>
                            </div>
                            <div className="flex items-center space-x-2">
                              <Button
                                size="sm"
                                variant="outline"
                                className="border-red-600 text-red-400 hover:bg-red-600 hover:text-white"
                              >
                                Block
                              </Button>
                              <Button
                                size="sm"
                                variant="outline"
                                className="border-blue-600 text-blue-400 hover:bg-blue-600 hover:text-white"
                              >
                                Investigate
                              </Button>
                              <Button size="sm" variant="ghost" className="text-gray-400 hover:text-white">
                                <X className="h-4 w-4" />
                              </Button>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Packet Details */}
                <div className="h-32 bg-[#2b2b2b]">
                  <div className="p-4">
                    <h3 className="text-sm font-semibold text-white mb-2">Packet Details</h3>
                    <div className="text-xs text-gray-400 font-mono">
                      <p>Frame 1: 1420 bytes on wire (11360 bits), 1420 bytes captured (11360 bits)</p>
                      <p>Ethernet II, Src: 00:1b:44:11:3a:b7, Dst: 00:50:56:c0:00:01</p>
                      <p>Internet Protocol Version 4, Src: 192.168.1.100, Dst: 8.8.8.8</p>
                      <p>Transmission Control Protocol, Src Port: 54321, Dst Port: 443</p>
                    </div>
                  </div>
                </div>
              </TabsContent>

              <TabsContent value="threats" className="flex-1 m-0 p-4">
                <div className="text-center text-gray-400 mt-8">
                  <AlertTriangle className="h-12 w-12 mx-auto mb-4" />
                  <p>Threat Analysis view would be implemented here</p>
                </div>
              </TabsContent>

              <TabsContent value="historical" className="flex-1 m-0 p-4">
                <div className="text-center text-gray-400 mt-8">
                  <Database className="h-12 w-12 mx-auto mb-4" />
                  <p>Historical Data view would be implemented here</p>
                </div>
              </TabsContent>
            </Tabs>
          </div>

          {/* Side Panel */}
          <div
            className={`${sidebarCollapsed ? "w-12" : "w-80"} bg-[#3c3c3c] border-l border-gray-700 transition-all duration-300`}
          >
            <div className="p-4">
              <div className="flex items-center justify-between mb-4">
                {!sidebarCollapsed && <h2 className="text-lg font-semibold text-white">Statistics</h2>}
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
                  className="text-gray-400 hover:text-white"
                >
                  {sidebarCollapsed ? <Maximize2 className="h-4 w-4" /> : <Minimize2 className="h-4 w-4" />}
                </Button>
              </div>

              {!sidebarCollapsed && (
                <ScrollArea className="h-[calc(100vh-200px)]">
                  <div className="space-y-6">
                    {/* Live Statistics */}
                    <Card className="bg-[#2b2b2b] border-gray-700">
                      <CardHeader className="pb-3">
                        <CardTitle className="text-sm text-gray-300 flex items-center">
                          <Activity className="h-4 w-4 mr-2" />
                          Live Statistics
                        </CardTitle>
                      </CardHeader>
                      <CardContent className="space-y-3">
                        <div className="flex justify-between items-center">
                          <span className="text-xs text-gray-400">Total Packets</span>
                          <span className="text-sm font-mono text-white">{totalPackets.toLocaleString()}</span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-xs text-gray-400">Data Rate</span>
                          <span className="text-sm font-mono text-white">2.4 MB/s</span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-xs text-gray-400">Active Threats</span>
                          <span className="text-sm font-mono text-red-400">3</span>
                        </div>
                        <div className="space-y-2">
                          <div className="flex justify-between text-xs">
                            <span className="text-gray-400">Memory Usage</span>
                            <span className="text-gray-300">68%</span>
                          </div>
                          <Progress value={68} className="h-2" />
                        </div>
                      </CardContent>
                    </Card>

                    {/* Quick Filters */}
                    <Card className="bg-[#2b2b2b] border-gray-700">
                      <CardHeader className="pb-3">
                        <CardTitle className="text-sm text-gray-300 flex items-center">
                          <Filter className="h-4 w-4 mr-2" />
                          Quick Filters
                        </CardTitle>
                      </CardHeader>
                      <CardContent className="space-y-2">
                        <div className="grid grid-cols-2 gap-2">
                          <Button
                            size="sm"
                            variant="outline"
                            className="border-gray-600 text-gray-300 hover:text-white text-xs"
                          >
                            HTTP
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            className="border-gray-600 text-gray-300 hover:text-white text-xs"
                          >
                            HTTPS
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            className="border-gray-600 text-gray-300 hover:text-white text-xs"
                          >
                            SSH
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            className="border-red-600 text-red-400 hover:bg-red-600 hover:text-white text-xs"
                          >
                            Threats
                          </Button>
                        </div>
                      </CardContent>
                    </Card>

                    {/* Blacklist Management */}
                    <Card className="bg-[#2b2b2b] border-gray-700">
                      <CardHeader className="pb-3">
                        <CardTitle className="text-sm text-gray-300 flex items-center">
                          <Lock className="h-4 w-4 mr-2" />
                          IP Management
                        </CardTitle>
                      </CardHeader>
                      <CardContent className="space-y-3">
                        <div className="space-y-2">
                          <div className="flex items-center justify-between">
                            <span className="text-xs text-gray-400">Blacklisted IPs</span>
                            <Badge variant="outline" className="text-xs border-red-600 text-red-400">
                              12
                            </Badge>
                          </div>
                          <div className="flex items-center justify-between">
                            <span className="text-xs text-gray-400">Whitelisted IPs</span>
                            <Badge variant="outline" className="text-xs border-green-600 text-green-400">
                              45
                            </Badge>
                          </div>
                        </div>
                        <div className="flex space-x-2">
                          <Button
                            size="sm"
                            variant="outline"
                            className="flex-1 border-gray-600 text-gray-300 hover:text-white text-xs"
                          >
                            <Plus className="h-3 w-3 mr-1" />
                            Add IP
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            className="border-gray-600 text-gray-300 hover:text-white"
                          >
                            <Settings className="h-3 w-3" />
                          </Button>
                        </div>
                      </CardContent>
                    </Card>

                    {/* Recent Activity */}
                    <Card className="bg-[#2b2b2b] border-gray-700">
                      <CardHeader className="pb-3">
                        <CardTitle className="text-sm text-gray-300 flex items-center">
                          <FileText className="h-4 w-4 mr-2" />
                          Recent Activity
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-2 text-xs">
                          <div className="flex items-center space-x-2">
                            <div className="w-2 h-2 bg-red-500 rounded-full"></div>
                            <span className="text-gray-400">14:23:45</span>
                            <span className="text-gray-300">Threat blocked</span>
                          </div>
                          <div className="flex items-center space-x-2">
                            <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
                            <span className="text-gray-400">14:23:40</span>
                            <span className="text-gray-300">Suspicious activity</span>
                          </div>
                          <div className="flex items-center space-x-2">
                            <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                            <span className="text-gray-400">14:23:35</span>
                            <span className="text-gray-300">Capture started</span>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  </div>
                </ScrollArea>
              )}
            </div>
          </div>
        </div>

        {/* Bottom Status Bar */}
        <div className="bg-[#1e1e1e] border-t border-gray-700 px-4 py-2">
          <div className="flex items-center justify-between text-xs text-gray-400">
            <div className="flex items-center space-x-6">
              <span>Status: {isCapturing ? "Capturing" : "Stopped"}</span>
              <span>Packets: {totalPackets.toLocaleString()}</span>
              <span>Rate: 2.4 MB/s</span>
              <span>Interface: {selectedInterface}</span>
            </div>
            <div className="flex items-center space-x-6">
              <span>Elapsed: 00:15:32</span>
              <div className="flex items-center space-x-2">
                <Cpu className="h-3 w-3" />
                <span>CPU: 12%</span>
              </div>
              <div className="flex items-center space-x-2">
                <HardDrive className="h-3 w-3" />
                <span>Memory: 68%</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </TooltipProvider>
  )
}
