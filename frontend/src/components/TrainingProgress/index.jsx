import React from 'react'
import { Progress, Card, Tag, Descriptions } from 'antd'

const TrainingProgress = ({ task }) => {
  if (!task) return null

  const getStatusColor = (status) => {
    const statusMap = {
      pending: 'default',
      running: 'processing',
      completed: 'success',
      failed: 'error',
      stopped: 'warning'
    }
    return statusMap[status] || 'default'
  }

  const getStatusText = (status) => {
    const statusMap = {
      pending: '等待中',
      running: '训练中',
      completed: '已完成',
      failed: '失败',
      stopped: '已停止'
    }
    return statusMap[status] || status
  }

  return (
    <Card title="训练进度">
      <Descriptions column={2} bordered>
        <Descriptions.Item label="任务名称">{task.name}</Descriptions.Item>
        <Descriptions.Item label="状态">
          <Tag color={getStatusColor(task.status)}>{getStatusText(task.status)}</Tag>
        </Descriptions.Item>
        <Descriptions.Item label="当前轮次">
          {task.current_epoch || 0} / {task.total_epochs || 0}
        </Descriptions.Item>
        <Descriptions.Item label="进度">
          <Progress percent={task.progress || 0} status={task.status === 'failed' ? 'exception' : 'active'} />
        </Descriptions.Item>
        <Descriptions.Item label="数据集路径" span={2}>
          {task.dataset_path}
        </Descriptions.Item>
        {task.metrics && (
          <>
            <Descriptions.Item label="mAP50">
              {task.metrics.mAP50 ? (task.metrics.mAP50 * 100).toFixed(2) + '%' : '-'}
            </Descriptions.Item>
            <Descriptions.Item label="mAP50-95">
              {task.metrics['mAP50-95'] ? (task.metrics['mAP50-95'] * 100).toFixed(2) + '%' : '-'}
            </Descriptions.Item>
          </>
        )}
        {task.error && (
          <Descriptions.Item label="错误信息" span={2}>
            <span style={{ color: 'red' }}>{task.error}</span>
          </Descriptions.Item>
        )}
      </Descriptions>
    </Card>
  )
}

export default TrainingProgress

