import React, { useState, useEffect } from 'react'
import { Card, Button, Modal, Form, Input, Upload, message, Space, Popconfirm, Tag } from 'antd'
import { PlusOutlined, UploadOutlined, CheckCircleOutlined } from '@ant-design/icons'
import { 
  getModels,
  getActiveModel,
  uploadModel,
  activateModel,
  deleteModel,
  downloadModel
} from '../../services/api'
import ModelList from '../../components/ModelList'

const { TextArea } = Input

function ModelsPage() {
  const [models, setModels] = useState([])
  const [loading, setLoading] = useState(false)
  const [modalVisible, setModalVisible] = useState(false)
  const [form] = Form.useForm()
  const [fileList, setFileList] = useState([])

  useEffect(() => {
    loadModels()
  }, [])

  const loadModels = async () => {
    setLoading(true)
    try {
      const response = await getModels()
      if (response.success && response.models) {
        setModels(response.models)
      } else {
        message.error(response.error || '加载模型列表失败')
      }
    } catch (error) {
      message.error('加载模型列表失败：' + (error.response?.data?.detail || error.message))
    } finally {
      setLoading(false)
    }
  }

  const handleUpload = async (values) => {
    if (fileList.length === 0) {
      message.warning('请选择模型文件')
      return
    }

    setLoading(true)
    try {
      const file = fileList[0].originFileObj
      const response = await uploadModel(
        file,
        values.name,
        values.description,
        values.training_task_id
      )
      if (response.success) {
        message.success('模型上传成功')
        setModalVisible(false)
        form.resetFields()
        setFileList([])
        loadModels()
      } else {
        message.error(response.error || '上传失败')
      }
    } catch (error) {
      message.error('上传失败：' + (error.response?.data?.detail || error.message))
    } finally {
      setLoading(false)
    }
  }

  const handleActivate = async (modelId) => {
    try {
      const response = await activateModel(modelId)
      if (response.success) {
        message.success('模型已激活')
        loadModels()
      } else {
        message.error('激活失败')
      }
    } catch (error) {
      message.error('激活失败：' + (error.response?.data?.detail || error.message))
    }
  }

  const handleDelete = async (modelId) => {
    try {
      const response = await deleteModel(modelId)
      if (response.success) {
        message.success('模型已删除')
        loadModels()
      } else {
        message.error('删除失败')
      }
    } catch (error) {
      message.error('删除失败：' + (error.response?.data?.detail || error.message))
    }
  }

  const handleDownload = async (modelId) => {
    try {
      const blob = await downloadModel(modelId)
      const model = models.find(m => m.id === modelId)
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = model ? model.filename : `model_${modelId}.pt`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
      message.success('下载成功')
    } catch (error) {
      message.error('下载失败：' + (error.response?.data?.detail || error.message))
    }
  }

  const uploadProps = {
    beforeUpload: (file) => {
      if (!file.name.endsWith('.pt')) {
        message.error('只支持.pt格式的模型文件')
        return false
      }
      setFileList([{ uid: '-1', name: file.name, originFileObj: file }])
      return false
    },
    fileList,
    maxCount: 1,
  }

  return (
    <div style={{ padding: '24px' }}>
      <Card
        title="模型管理"
        extra={
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => setModalVisible(true)}
          >
            上传模型
          </Button>
        }
      >
        {models.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '40px' }}>
            <p>暂无模型，请上传模型文件</p>
          </div>
        ) : (
          <ModelList
            models={models}
            onActivate={handleActivate}
            onDelete={handleDelete}
            onDownload={handleDownload}
          />
        )}
      </Card>

      <Modal
        title="上传模型"
        open={modalVisible}
        onCancel={() => {
          setModalVisible(false)
          form.resetFields()
          setFileList([])
        }}
        onOk={() => form.submit()}
        okText="上传"
        cancelText="取消"
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleUpload}
        >
          <Form.Item
            name="file"
            label="模型文件"
            rules={[{ required: true, message: '请选择模型文件' }]}
          >
            <Upload {...uploadProps}>
              <Button icon={<UploadOutlined />}>选择文件</Button>
              <span style={{ marginLeft: 8 }}>只支持.pt格式</span>
            </Upload>
          </Form.Item>
          <Form.Item
            name="name"
            label="模型名称"
            rules={[{ required: true, message: '请输入模型名称' }]}
          >
            <Input placeholder="请输入模型名称" />
          </Form.Item>
          <Form.Item
            name="description"
            label="模型描述"
          >
            <TextArea rows={4} placeholder="请输入模型描述（可选）" />
          </Form.Item>
          <Form.Item
            name="training_task_id"
            label="关联训练任务ID（可选）"
          >
            <Input placeholder="如果模型来自训练任务，请输入任务ID" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default ModelsPage

