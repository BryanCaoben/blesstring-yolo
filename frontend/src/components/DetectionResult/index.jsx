import React, { useEffect, useRef } from 'react'
import { Card, Tag, Space, Typography } from 'antd'
import { CheckCircleOutlined } from '@ant-design/icons'

const { Title, Text } = Typography

const DetectionResult = ({ imagePath, defects }) => {
  const canvasRef = useRef(null)
  const imageRef = useRef(null)

  useEffect(() => {
    if (!imagePath) return

    const canvas = canvasRef.current
    if (!canvas) return
    
    const ctx = canvas.getContext('2d')
    const img = new Image()
    img.crossOrigin = 'anonymous'
    
    img.onload = () => {
      canvas.width = img.width
      canvas.height = img.height
      ctx.drawImage(img, 0, 0)
      
      // 如果有瑕疵，绘制检测框
      if (defects && defects.length > 0) {
        defects.forEach((defect, index) => {
          const { x1, y1, x2, y2, confidence, class_name } = defect
          const width = x2 - x1
          const height = y2 - y1
          
          // 绘制矩形框
          ctx.strokeStyle = '#ff4d4f'
          ctx.lineWidth = 3
          ctx.strokeRect(x1, y1, width, height)
          
          // 绘制标签
          ctx.fillStyle = '#ff4d4f'
          ctx.font = '16px Arial'
          const label = `${class_name} ${(confidence * 100).toFixed(1)}%`
          const textWidth = ctx.measureText(label).width
          ctx.fillRect(x1, y1 - 25, textWidth + 10, 25)
          ctx.fillStyle = '#fff'
          ctx.fillText(label, x1 + 5, y1 - 7)
        })
      }
    }
    
    img.onerror = () => {
      console.error('图片加载失败:', imagePath)
    }
    
    // 从file_path中提取文件名
    const filename = imagePath.split(/[/\\]/).pop()
    img.src = `/static/${filename}`
    imageRef.current = img
  }, [imagePath, defects])

  if (!defects || defects.length === 0) {
    return (
      <Card>
        <Space direction="vertical" style={{ width: '100%' }}>
          <Space>
            <CheckCircleOutlined style={{ color: '#52c41a', fontSize: '24px' }} />
            <Text strong>未检测到瑕疵，乐器状态良好！</Text>
          </Space>
          {imagePath && (
            <div style={{ marginTop: '16px', textAlign: 'center' }}>
              <img 
                src={`/static/${imagePath.split(/[/\\]/).pop()}`}
                alt="检测图片"
                style={{ 
                  maxWidth: '100%', 
                  height: 'auto',
                  border: '1px solid #d9d9d9',
                  borderRadius: '4px'
                }}
                onError={(e) => {
                  e.target.style.display = 'none'
                }}
              />
            </div>
          )}
        </Space>
      </Card>
    )
  }

  return (
    <Card>
      <Title level={4}>检测结果</Title>
      <Space direction="vertical" style={{ width: '100%' }}>
        <div>
          <Text strong>检测到 {defects.length} 个瑕疵：</Text>
          <div style={{ marginTop: '8px' }}>
            {defects.map((defect, index) => (
              <Tag key={index} color="red" style={{ marginBottom: '4px' }}>
                {defect.class_name} - 置信度: {(defect.confidence * 100).toFixed(1)}%
              </Tag>
            ))}
          </div>
        </div>
        <div style={{ marginTop: '16px', textAlign: 'center' }}>
          <canvas 
            ref={canvasRef} 
            style={{ 
              maxWidth: '100%', 
              height: 'auto',
              border: '1px solid #d9d9d9',
              borderRadius: '4px'
            }} 
          />
        </div>
      </Space>
    </Card>
  )
}

export default DetectionResult

