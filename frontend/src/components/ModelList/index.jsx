import React from 'react'
import { Card, Tag, Descriptions, Space } from 'antd'
import { CheckCircleOutlined } from '@ant-design/icons'

const ModelList = ({ models, onActivate, onDelete, onDownload }) => {
  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
  }

  return (
    <Space direction="vertical" style={{ width: '100%' }} size="large">
      {models.map((model) => (
        <Card
          key={model.id}
          title={
            <Space>
              {model.name}
              {model.is_active && (
                <Tag color="green" icon={<CheckCircleOutlined />}>
                  当前使用
                </Tag>
              )}
            </Space>
          }
          extra={
            <Space>
              {!model.is_active && (
                <a onClick={() => onActivate(model.id)}>激活</a>
              )}
              <a onClick={() => onDownload(model.id)}>下载</a>
              {!model.is_active && (
                <a onClick={() => onDelete(model.id)} style={{ color: 'red' }}>
                  删除
                </a>
              )}
            </Space>
          }
        >
          <Descriptions column={2} size="small">
            <Descriptions.Item label="文件名">{model.filename}</Descriptions.Item>
            <Descriptions.Item label="文件大小">
              {formatFileSize(model.file_size)}
            </Descriptions.Item>
            {model.version && (
              <Descriptions.Item label="版本">{model.version}</Descriptions.Item>
            )}
            {model.accuracy !== null && (
              <Descriptions.Item label="准确率">
                {(model.accuracy * 100).toFixed(2)}%
              </Descriptions.Item>
            )}
            {model.mAP !== null && (
              <Descriptions.Item label="mAP">
                {(model.mAP * 100).toFixed(2)}%
              </Descriptions.Item>
            )}
            {model.trained_at && (
              <Descriptions.Item label="训练时间">
                {new Date(model.trained_at).toLocaleString('zh-CN')}
              </Descriptions.Item>
            )}
            <Descriptions.Item label="创建时间">
              {new Date(model.created_at).toLocaleString('zh-CN')}
            </Descriptions.Item>
            {model.description && (
              <Descriptions.Item label="描述" span={2}>
                {model.description}
              </Descriptions.Item>
            )}
          </Descriptions>
        </Card>
      ))}
    </Space>
  )
}

export default ModelList

