'use client'

import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { format } from 'date-fns'
import { useEffect, useState } from 'react'

interface LogEntry {
  id: string
  timestamp: string
  level: 'INFO' | 'WARN' | 'ERROR' | 'DEBUG'
  message: string
  module: string
  userId?: string
  ip?: string
}

export default function AdminLogsPage() {
  const [logs, setLogs] = useState<LogEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('')
  const [levelFilter, setLevelFilter] = useState<string>('')

  useEffect(() => {
    fetchLogs()
  }, [])

  const fetchLogs = async () => {
    try {
      setLoading(true)
      // API 호출 대신 임시 데이터 사용
      const mockLogs: LogEntry[] = [
        {
          id: '1',
          timestamp: new Date().toISOString(),
          level: 'INFO',
          message: 'User login successful',
          module: 'auth',
          userId: 'user123',
          ip: '192.168.1.1'
        },
        {
          id: '2',
          timestamp: new Date(Date.now() - 1000 * 60 * 5).toISOString(),
          level: 'WARN',
          message: 'High memory usage detected',
          module: 'system',
          ip: '127.0.0.1'
        },
        {
          id: '3',
          timestamp: new Date(Date.now() - 1000 * 60 * 10).toISOString(),
          level: 'ERROR',
          message: 'Database connection failed',
          module: 'database',
          ip: '127.0.0.1'
        }
      ]
      setLogs(mockLogs)
    } catch (error) {
      console.error('Failed to fetch logs:', error)
    } finally {
      setLoading(false)
    }
  }

  const filteredLogs = logs.filter(log => {
    const matchesText = log.message.toLowerCase().includes(filter.toLowerCase()) ||
                       log.module.toLowerCase().includes(filter.toLowerCase())
    const matchesLevel = levelFilter === '' || log.level === levelFilter
    return matchesText && matchesLevel
  })

  const getLevelBadgeColor = (level: string) => {
    switch (level) {
      case 'ERROR': return 'destructive'
      case 'WARN': return 'secondary'
      case 'INFO': return 'default'
      case 'DEBUG': return 'outline'
      default: return 'default'
    }
  }

  return (
    <div className="container mx-auto py-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">시스템 로그</h1>
        <Button onClick={fetchLogs} disabled={loading}>
          새로고침
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>로그 필터</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex space-x-4">
            <Input
              placeholder="메시지 또는 모듈 검색..."
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className="flex-1"
            />
            <Select value={levelFilter} onValueChange={setLevelFilter}>
              <SelectTrigger className="w-32">
                <SelectValue placeholder="레벨" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">전체</SelectItem>
                <SelectItem value="ERROR">ERROR</SelectItem>
                <SelectItem value="WARN">WARN</SelectItem>
                <SelectItem value="INFO">INFO</SelectItem>
                <SelectItem value="DEBUG">DEBUG</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>로그 목록 ({filteredLogs.length})</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8">로그를 불러오는 중...</div>
          ) : filteredLogs.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              조건에 맞는 로그가 없습니다.
            </div>
          ) : (
            <div className="space-y-2">
              {filteredLogs.map((log) => (
                <div
                  key={log.id}
                  className="border rounded-lg p-4 hover:bg-muted/50 transition-colors"
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-2">
                      <Badge variant={getLevelBadgeColor(log.level)}>
                        {log.level}
                      </Badge>
                      <span className="text-sm text-muted-foreground">
                        {log.module}
                      </span>
                    </div>
                    <span className="text-sm text-muted-foreground">
                      {format(new Date(log.timestamp), 'yyyy-MM-dd HH:mm:ss')}
                    </span>
                  </div>
                  <p className="text-sm mb-2">{log.message}</p>
                  <div className="flex justify-between text-xs text-muted-foreground">
                    <span>ID: {log.id}</span>
                    <div className="space-x-4">
                      {log.userId && <span>User: {log.userId}</span>}
                      {log.ip && <span>IP: {log.ip}</span>}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
