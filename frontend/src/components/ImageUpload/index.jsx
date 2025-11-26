import React from 'react'
import { Upload, message } from 'antd'
import { InboxOutlined } from '@ant-design/icons'
import { uploadImage } from '../../services/api'

const { Dragger } = Upload

const ImageUpload = ({ onUploadSuccess }) => {
  const props = {
    name: 'file',
    multiple: false,
    accept: 'image/*',
    customRequest: async ({ file, onSuccess, onError }) => {
      try {
        const result = await uploadImage(file)
        message.success('上传成功！')
        onSuccess(result, file)
        if (onUploadSuccess) {
          onUploadSuccess(result)
        }
      } catch (error) {
        message.error('上传失败：' + (error.response?.data?.detail || error.message))
        onError(error)
      }
    },
    showUploadList: {
      showPreviewIcon: false,
      showRemoveIcon: true,
    },
  }

  return (
    <Dragger {...props} style={{ padding: '20px' }}>
      <p className="ant-upload-drag-icon">
        <InboxOutlined />
      </p>
      <p className="ant-upload-text">点击或拖拽图片到此区域上传</p>
      <p className="ant-upload-hint">
        支持 JPG、PNG、JPEG 格式，用于检测乐器瑕疵
      </p>
    </Dragger>
  )
}

export default ImageUpload

