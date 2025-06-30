"use client";

import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  LineChart, Line, AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer 
} from 'recharts';
import { 
  Shield, Activity, Users, Database, Wifi, AlertTriangle, 
  CheckCircle, XCircle, TrendingUp, Network, Eye, Settings 
} from 'lucide-react';

// Custom hook for WebSocket connection
const useWebSocket = (url, onMessage) => {
  const [socket, setSocket] = useState(null);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    const ws = new WebSocket(url);
    
    ws.onopen = () => {
      setConnected(true);
      console.log('WebSocket connected');
    };
    
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        onMessage(data);
      } catch (error) {
        console.error('WebSocket message parse error:', error);
      }
    };
    
    ws.onclose = () => {
      setConnected(false);
      console.log('WebSocket disconnected');
    };
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setConnected(false);
    };
    
    setSocket(ws);
    
    return () => {
      ws.close();
    };
  }, [url, onMessage]);

  return { socket, connected };
};

// API service
const apiService = {
  baseURL: 'http://127.0.0.1:8000/api',
  auth: { username: 'admin', password: 'cybersnoop2025' },
  
  async request(endpoint) {
    try {
      const response = await fetch(`${this.baseURL}${endpoint}`, {
        headers: {
          'Authorization': `Basic ${btoa(`${this.auth.username}:${this.auth.password}`)}`
        }
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error(`API request failed for ${endpoint}:`, error);
      throw error;
    }
  },
  
  getStatus: () => apiService.request('/status'),
  getStats: () => apiService.request('/stats'),
  getInterfaces: () => apiService.request('/interfaces'),
  getPackets: (limit = 100) => apiService.request(`/packets?limit=${limit}`),
  getThreats: (limit = 50) => apiService.request(`/threats?limit=${limit}`),
  startMonitoring: () => apiService.request('/monitoring/start'),
  stopMonitoring: () => apiService.request('/monitoring/stop')
};

const CyberSnoopDashboard = () => {
  // State management
  const [systemStatus, setSystemStatus] = useState({
    status: 'loading',
    monitoring: false,
    interfaces: 0,
    uptime: '00:00:00'
  });
  
  const [networkStats, setNetworkStats] = useState({
    packets_captured: 0,
    threats_detected: 0,
    active_connections: 0,
    network_interfaces: 0,
    bandwidth_usage: { upload: '0 B/s', download: '0 B/s' }
  });
  
  const [recentPackets, setRecentPackets] = useState([]);
  const [recentThreats, setRecentThreats] = useState([]);
  const [interfaces, setInterfaces] = useState([]);
  const [chartData, setChartData] = useState([]);
  const [threatDistribution, setThreatDistribution] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [darkMode, setDarkMode] = useState(true);

  // WebSocket message handler
  const handleWebSocketMessage = useCallback((data) => {
    if (data.type === 'stats_update') {
      setNetworkStats(prev => ({
        ...prev,
        packets_captured: data.data.packets || prev.packets_captured,
        threats_detected: data.data.threats || prev.threats_detected,
        monitoring: data.data.monitoring || prev.monitoring
      }));
      
      // Update chart data for real-time visualization
      setChartData(prev => {
        const newData = {
          time: new Date().toLocaleTimeString(),
          packets: data.data.packets || 0,
          threats: data.data.threats || 0,
          timestamp: Date.now()
        };
        
        const updatedData = [...prev, newData];
        // Keep only last 20 data points
        return updatedData.slice(-20);
      });
    }
  }, []);

  // WebSocket connection
  const { connected: wsConnected } = useWebSocket('ws://127.0.0.1:8000/ws', handleWebSocketMessage);

  // Load initial data
  const loadData = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      const [statusData, statsData, interfacesData, packetsData, threatsData] = await Promise.all([
        apiService.getStatus(),
        apiService.getStats(),
        apiService.getInterfaces(),
        apiService.getPackets(20),
        apiService.getThreats(10)
      ]);
      
      setSystemStatus(statusData);
      setNetworkStats(statsData);
      setInterfaces(interfacesData.interfaces || []);
      setRecentPackets(packetsData.packets || []);
      setRecentThreats(threatsData.threats || []);
      
      // Process threat distribution
      const threatTypes = {};
      (threatsData.threats || []).forEach(threat => {
        threatTypes[threat.threat_type] = (threatTypes[threat.threat_type] || 0) + 1;
      });
      
      setThreatDistribution(
        Object.entries(threatTypes).map(([type, count]) => ({
          name: type,
          value: count,
          color: getThreatColor(type)
        }))
      );
      
    } catch (error) {
      console.error('Failed to load data:', error);
      setError('Failed to connect to CyberSnoop API. Please ensure the server is running.');
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Load data on component mount and set up periodic refresh
  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, [loadData]);

  // Utility functions
  const getThreatColor = (threatType) => {
    const colors = {
      'port_scan': '#ff6b6b',
      'brute_force': '#ff8e53',
      'ddos_attack': '#ff6b9d',
      'malware': '#c44569',
      'anomaly': '#f8b500',
      'exfiltration': '#e55039'
    };
    return colors[threatType] || '#6c5ce7';
  };

  const getSeverityColor = (severity) => {
    switch (severity?.toLowerCase()) {
      case 'critical': return 'destructive';
      case 'high': return 'destructive';
      case 'medium': return 'default';
      case 'low': return 'secondary';
      default: return 'outline';
    }
  };

  const formatUptime = (uptime) => {
    return uptime || '00:00:00';
  };

  // Control functions
  const toggleMonitoring = async () => {
    try {
      if (systemStatus.monitoring) {
        await apiService.stopMonitoring();
      } else {
        await apiService.startMonitoring();
      }
      await loadData(); // Refresh data
    } catch (error) {
      console.error('Failed to toggle monitoring:', error);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-900">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-300">Loading CyberSnoop Dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-900">
        <Alert className="max-w-md">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
          <Button onClick={loadData} className="mt-2">Retry</Button>
        </Alert>
      </div>
    );
  }

  return (
    <div className={`min-h-screen ${darkMode ? 'dark bg-gray-900' : 'bg-gray-50'}`}>
      {/* Header */}
      <header className="bg-gray-800 border-b border-gray-700 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Shield className="h-8 w-8 text-blue-500" />
            <div>
              <h1 className="text-xl font-bold text-white">CyberSnoop</h1>
              <p className="text-sm text-gray-400">Network Security Monitor</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <div className={`h-2 w-2 rounded-full ${wsConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
              <span className="text-sm text-gray-400">
                {wsConnected ? 'Live' : 'Disconnected'}
              </span>
            </div>
            
            <Button
              onClick={toggleMonitoring}
              variant={systemStatus.monitoring ? 'destructive' : 'default'}
              size="sm"
            >
              {systemStatus.monitoring ? 'Stop Monitoring' : 'Start Monitoring'}
            </Button>
            
            <Button
              onClick={() => setDarkMode(!darkMode)}
              variant="outline"
              size="sm"
            >
              <Settings className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </header>

      <div className="p-6 space-y-6">
        {/* Status Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">System Status</CardTitle>
              <Activity className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="flex items-center space-x-2">
                {systemStatus.monitoring ? (
                  <CheckCircle className="h-5 w-5 text-green-500" />
                ) : (
                  <XCircle className="h-5 w-5 text-red-500" />
                )}
                <span className="text-lg font-bold">
                  {systemStatus.monitoring ? 'Active' : 'Inactive'}
                </span>
              </div>
              <p className="text-xs text-muted-foreground mt-1">
                Uptime: {formatUptime(systemStatus.uptime)}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Packets Captured</CardTitle>
              <Database className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{networkStats.packets_captured.toLocaleString()}</div>
              <p className="text-xs text-muted-foreground">
                Total packets processed
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Threats Detected</CardTitle>
              <AlertTriangle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-500">{networkStats.threats_detected}</div>
              <p className="text-xs text-muted-foreground">
                Security alerts generated
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Network Interfaces</CardTitle>
              <Network className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{networkStats.network_interfaces}</div>
              <p className="text-xs text-muted-foreground">
                Active network adapters
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Real-time Activity Chart */}
          <Card>
            <CardHeader>
              <CardTitle>Real-time Activity</CardTitle>
              <CardDescription>Live packet and threat detection</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="time" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="packets" stroke="#3b82f6" strokeWidth={2} />
                  <Line type="monotone" dataKey="threats" stroke="#ef4444" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Threat Distribution */}
          <Card>
            <CardHeader>
              <CardTitle>Threat Distribution</CardTitle>
              <CardDescription>Types of detected threats</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={threatDistribution}
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                    label={({name, value}) => `${name}: ${value}`}
                  >
                    {threatDistribution.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>

        {/* Recent Activity Tables */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Recent Threats */}
          <Card>
            <CardHeader>
              <CardTitle>Recent Threats</CardTitle>
              <CardDescription>Latest security alerts</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {recentThreats.length > 0 ? (
                  recentThreats.slice(0, 5).map((threat, index) => (
                    <div key={index} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2">
                          <Badge variant={getSeverityColor(threat.severity)}>
                            {threat.severity || 'Unknown'}
                          </Badge>
                          <span className="font-medium">{threat.threat_type}</span>
                        </div>
                        <p className="text-sm text-muted-foreground mt-1">
                          From: {threat.source_ip} | {new Date(threat.timestamp).toLocaleTimeString()}
                        </p>
                      </div>
                      <AlertTriangle className="h-5 w-5 text-red-500" />
                    </div>
                  ))
                ) : (
                  <p className="text-center text-muted-foreground py-8">No recent threats detected</p>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Recent Packets */}
          <Card>
            <CardHeader>
              <CardTitle>Recent Packets</CardTitle>
              <CardDescription>Latest network traffic</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {recentPackets.length > 0 ? (
                  recentPackets.slice(0, 5).map((packet, index) => (
                    <div key={index} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2">
                          <Badge variant="outline">{packet.protocol}</Badge>
                          <span className="font-medium">{packet.category}</span>
                        </div>
                        <p className="text-sm text-muted-foreground mt-1">
                          {packet.src_ip}:{packet.src_port} → {packet.dst_ip}:{packet.dst_port}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          {new Date(packet.timestamp).toLocaleTimeString()} | {packet.size} bytes
                        </p>
                      </div>
                    </div>
                  ))
                ) : (
                  <p className="text-center text-muted-foreground py-8">No recent packets captured</p>
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Network Interfaces */}
        <Card>
          <CardHeader>
            <CardTitle>Network Interfaces</CardTitle>
            <CardDescription>Active network adapters and their status</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {interfaces.length > 0 ? (
                interfaces.map((iface, index) => (
                  <div key={index} className="p-4 border rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-medium">{iface.name}</h4>
                      <Badge variant={iface.status === 'Up' ? 'default' : 'secondary'}>
                        {iface.status}
                      </Badge>
                    </div>
                    <p className="text-sm text-muted-foreground mb-1">
                      IP: {iface.ip || 'Not assigned'}
                    </p>
                    <p className="text-sm text-muted-foreground mb-1">
                      MAC: {iface.mac || 'Unknown'}
                    </p>
                    <p className="text-sm text-muted-foreground">
                      Speed: {iface.speed || 'Unknown'}
                    </p>
                  </div>
                ))
              ) : (
                <p className="text-center text-muted-foreground py-8 col-span-full">
                  No network interfaces detected
                </p>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default CyberSnoopDashboard;
