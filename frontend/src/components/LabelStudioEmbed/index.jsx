import React from 'react'
import { Card, Spin } from 'antd'

const LabelStudioEmbed = ({ projectId, labelStudioUrl }) => {
  const embedUrl = projectId 
    ? `${labelStudioUrl}/projects/${projectId}/` 
    : `${labelStudioUrl}/projects/`

  return (
    <Card>
      <div style={{ position: 'relative', minHeight: '600px' }}>
        <iframe
          src={embedUrl}
          style={{
            width: '100%',
            height: '800px',
            border: 'none',
            borderRadius: '4px'
          }}
          title="LabelStudio标注界面"
          onLoad={() => {
            // iframe加载完成
          }}
        />
      </div>
    </Card>
  )
}

export default LabelStudioEmbed

