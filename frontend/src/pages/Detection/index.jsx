import React, { useState } from 'react'
import { Card, Button, Spin, message, Space } from 'antd'
import { ReloadOutlined } from '@ant-design/icons'
import ImageUpload from '../../components/ImageUpload'
import DetectionResult from '../../components/DetectionResult'
import { detectDefects } from '../../services/api'

function DetectionPage() {
  const [uploadedFile, setUploadedFile] = useState(null)
  const [detectionResult, setDetectionResult] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleUploadSuccess = (result) => {
    setUploadedFile(result)
    setDetectionResult(null)
  }

  const handleDetect = async () => {
    if (!uploadedFile) {
      message.warning('请先上传图片')
      return
    }

    setLoading(true)
    try {
      const result = await detectDefects(uploadedFile.file_path)
      if (result.success) {
        setDetectionResult(result.result)
        message.success('检测完成！')
      } else {
        message.error('检测失败：' + (result.error || '未知错误'))
      }
    } catch (error) {
      message.error('检测失败：' + (error.response?.data?.detail || error.message))
    } finally {
      setLoading(false)
    }
  }

  const handleReset = () => {
    setUploadedFile(null)
    setDetectionResult(null)
  }

  return (
    <div style={{ padding: '24px' }}>
      <Card style={{ marginBottom: '24px' }} title="上传图片">
        <ImageUpload onUploadSuccess={handleUploadSuccess} />
      </Card>

      {uploadedFile && (
        <Card title="检测操作">
          <div style={{ marginBottom: '16px' }}>
            <Space>
              <Button
                type="primary"
                onClick={handleDetect}
                loading={loading}
                size="large"
              >
                开始检测
              </Button>
              <Button onClick={handleReset} icon={<ReloadOutlined />}>
                重新上传
              </Button>
            </Space>
          </div>

          {loading && (
            <div style={{ textAlign: 'center', padding: '40px' }}>
              <Spin size="large" />
              <p style={{ marginTop: '16px' }}>正在检测中，请稍候...</p>
            </div>
          )}

          {detectionResult && !loading && (
            <DetectionResult
              imagePath={detectionResult.image_path}
              defects={detectionResult.defects}
            />
          )}
        </Card>
      )}
    </div>
  )
}

export default DetectionPage

