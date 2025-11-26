import React, { useState, useEffect } from 'react'
import { Card, Table, Button, Modal, Input, Form, message, Space, Popconfirm, Tag, Alert, Typography } from 'antd'
import { PlusOutlined, DeleteOutlined, ExportOutlined, EyeOutlined, InfoCircleOutlined } from '@ant-design/icons'
import { 
  getLabelStudioProjects, 
  createLabelStudioProject, 
  deleteLabelStudioProject,
  getLabelStudioProjectUrl,
  exportLabelStudioProject
} from '../../services/api'
import LabelStudioEmbed from '../../components/LabelStudioEmbed'

const { TextArea } = Input

function AnnotationPage() {
  const [projects, setProjects] = useState([])
  const [loading, setLoading] = useState(false)
  const [modalVisible, setModalVisible] = useState(false)
  const [embedVisible, setEmbedVisible] = useState(false)
  const [selectedProject, setSelectedProject] = useState(null)
  const [form] = Form.useForm()
  const [labelStudioUrl, setLabelStudioUrl] = useState('http://localhost:8080')

  useEffect(() => {
    loadProjects()
  }, [])

  const loadProjects = async () => {
    setLoading(true)
    try {
      const response = await getLabelStudioProjects()
      if (response.success && response.tasks) {
        setProjects(response.tasks)
      } else {
        message.error(response.error || '加载项目列表失败')
      }
    } catch (error) {
      message.error('加载项目列表失败：' + (error.response?.data?.detail || error.message))
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = async (values) => {
    try {
      const response = await createLabelStudioProject({
        title: values.title,
        description: values.description
      })
      if (response.success) {
        message.success('项目创建成功')
        setModalVisible(false)
        form.resetFields()
        loadProjects()
      } else {
        message.error(response.error || '创建项目失败')
      }
    } catch (error) {
      message.error('创建项目失败：' + (error.response?.data?.detail || error.message))
    }
  }

  const handleDelete = async (projectId) => {
    try {
      const response = await deleteLabelStudioProject(projectId)
      if (response.success) {
        message.success('项目已删除')
        loadProjects()
      } else {
        message.error('删除项目失败')
      }
    } catch (error) {
      message.error('删除项目失败：' + (error.response?.data?.detail || error.message))
    }
  }

  const handleView = async (project) => {
    try {
      const response = await getLabelStudioProjectUrl(project.id)
      if (response.success) {
        setLabelStudioUrl(response.url.replace(/\/projects\/\d+.*/, ''))
        setSelectedProject(project)
        setEmbedVisible(true)
      }
    } catch (error) {
      message.error('获取项目URL失败')
    }
  }

  const handleExport = async (projectId) => {
    try {
      const blob = await exportLabelStudioProject(projectId, 'YOLO')
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `project_${projectId}_YOLO.zip`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
      message.success('导出成功')
    } catch (error) {
      message.error('导出失败：' + (error.response?.data?.detail || error.message))
    }
  }

  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 80,
    },
    {
      title: '项目名称',
      dataIndex: 'title',
      key: 'title',
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (text) => text ? new Date(text).toLocaleString('zh-CN') : '-',
    },
    {
      title: '操作',
      key: 'action',
      width: 250,
      render: (_, record) => (
        <Space>
          <Button
            type="link"
            icon={<EyeOutlined />}
            onClick={() => handleView(record)}
          >
            打开标注
          </Button>
          <Button
            type="link"
            icon={<ExportOutlined />}
            onClick={() => handleExport(record.id)}
          >
            导出
          </Button>
          <Popconfirm
            title="确定要删除这个项目吗？"
            onConfirm={() => handleDelete(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Button
              type="link"
              danger
              icon={<DeleteOutlined />}
            >
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ]

  const { Paragraph, Text } = Typography

  return (
    <div style={{ padding: '24px' }}>
      <Alert
        message="自动分割功能说明"
        description={
          <div>
            <Paragraph>
              已集成YOLOv8分割模型的自动预标注功能。要在LabelStudio中使用自动分割：
            </Paragraph>
            <Paragraph>
              1. 在LabelStudio项目设置中，添加ML后端URL：<Text code>http://your-server-ip:8000/api/v1/ml</Text>
            </Paragraph>
            <Paragraph>
              2. 上传图片到LabelStudio项目时，系统会自动运行分割模型进行预标注
            </Paragraph>
            <Paragraph>
              3. 你只需检查和微调预标注结果即可，大大提高标注效率！
            </Paragraph>
          </div>
        }
        type="info"
        icon={<InfoCircleOutlined />}
        showIcon
        style={{ marginBottom: '24px' }}
      />
      <Card
        title="标注项目管理"
        extra={
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => setModalVisible(true)}
          >
            创建项目
          </Button>
        }
      >
        <Table
          columns={columns}
          dataSource={projects}
          rowKey="id"
          loading={loading}
          pagination={{ pageSize: 10 }}
        />
      </Card>

      <Modal
        title="创建标注项目"
        open={modalVisible}
        onCancel={() => {
          setModalVisible(false)
          form.resetFields()
        }}
        onOk={() => form.submit()}
        okText="创建"
        cancelText="取消"
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleCreate}
        >
          <Form.Item
            name="title"
            label="项目名称"
            rules={[{ required: true, message: '请输入项目名称' }]}
          >
            <Input placeholder="请输入项目名称" />
          </Form.Item>
          <Form.Item
            name="description"
            label="项目描述"
          >
            <TextArea rows={4} placeholder="请输入项目描述（可选）" />
          </Form.Item>
        </Form>
      </Modal>

      <Modal
        title={`标注界面 - ${selectedProject?.title || ''}`}
        open={embedVisible}
        onCancel={() => {
          setEmbedVisible(false)
          setSelectedProject(null)
        }}
        footer={null}
        width="95%"
        style={{ top: 20 }}
      >
        {selectedProject && (
          <LabelStudioEmbed
            projectId={selectedProject.id}
            labelStudioUrl={labelStudioUrl}
          />
        )}
      </Modal>
    </div>
  )
}

export default AnnotationPage

