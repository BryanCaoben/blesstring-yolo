import React, { useState, useEffect } from 'react'
import { Card, Table, Button, Modal, Form, Input, Upload, message, Space, Popconfirm, Tag, Progress } from 'antd'
import { PlusOutlined, DeleteOutlined, PlayCircleOutlined, StopOutlined, UploadOutlined } from '@ant-design/icons'
import { 
  getTrainingTasks, 
  createTrainingTask, 
  startTraining,
  stopTraining,
  deleteTrainingTask,
  uploadDataset
} from '../../services/api'
import TrainingProgress from '../../components/TrainingProgress'

const { TextArea } = Input

function TrainingPage() {
  const [tasks, setTasks] = useState([])
  const [loading, setLoading] = useState(false)
  const [modalVisible, setModalVisible] = useState(false)
  const [detailVisible, setDetailVisible] = useState(false)
  const [selectedTask, setSelectedTask] = useState(null)
  const [form] = Form.useForm()
  const [pollingInterval, setPollingInterval] = useState(null)

  useEffect(() => {
    loadTasks()
    // 开始轮询正在运行的任务
    const interval = setInterval(() => {
      loadTasks()
    }, 5000) // 每5秒刷新一次
    setPollingInterval(interval)
    return () => {
      if (interval) clearInterval(interval)
    }
  }, [])

  const loadTasks = async () => {
    try {
      const response = await getTrainingTasks()
      if (response.success && response.tasks) {
        setTasks(response.tasks)
        // 如果有正在运行的任务，更新详情
        if (selectedTask && selectedTask.status === 'running') {
          const updated = response.tasks.find(t => t.id === selectedTask.id)
          if (updated) setSelectedTask(updated)
        }
      }
    } catch (error) {
      console.error('加载训练任务失败:', error)
    }
  }

  const handleCreate = async (values) => {
    setLoading(true)
    try {
      const response = await createTrainingTask({
        name: values.name,
        dataset_path: values.dataset_path,
        config: {
          epochs: values.epochs || 100,
          batch_size: values.batch_size || 16,
          img_size: values.img_size || 640,
          learning_rate: values.learning_rate || 0.01,
          device: values.device || 'cpu'
        }
      })
      if (response.success) {
        message.success('训练任务创建成功')
        setModalVisible(false)
        form.resetFields()
        loadTasks()
      } else {
        message.error(response.error || '创建任务失败')
      }
    } catch (error) {
      message.error('创建任务失败：' + (error.response?.data?.detail || error.message))
    } finally {
      setLoading(false)
    }
  }

  const handleStart = async (taskId) => {
    try {
      const response = await startTraining(taskId)
      if (response.success) {
        message.success('训练任务已启动')
        loadTasks()
      } else {
        message.error(response.error || '启动任务失败')
      }
    } catch (error) {
      message.error('启动任务失败：' + (error.response?.data?.detail || error.message))
    }
  }

  const handleStop = async (taskId) => {
    try {
      const response = await stopTraining(taskId)
      if (response.success) {
        message.success('训练任务已停止')
        loadTasks()
      } else {
        message.error('停止任务失败')
      }
    } catch (error) {
      message.error('停止任务失败：' + (error.response?.data?.detail || error.message))
    }
  }

  const handleDelete = async (taskId) => {
    try {
      const response = await deleteTrainingTask(taskId)
      if (response.success) {
        message.success('任务已删除')
        loadTasks()
        if (selectedTask && selectedTask.id === taskId) {
          setDetailVisible(false)
          setSelectedTask(null)
        }
      } else {
        message.error('删除任务失败')
      }
    } catch (error) {
      message.error('删除任务失败：' + (error.response?.data?.detail || error.message))
    }
  }

  const handleViewDetail = async (task) => {
    setSelectedTask(task)
    setDetailVisible(true)
  }

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

  const columns = [
    {
      title: '任务名称',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status) => (
        <Tag color={getStatusColor(status)}>{getStatusText(status)}</Tag>
      ),
    },
    {
      title: '进度',
      key: 'progress',
      render: (_, record) => (
        <Progress 
          percent={record.progress || 0} 
          size="small"
          status={record.status === 'failed' ? 'exception' : 'active'}
        />
      ),
    },
    {
      title: '当前轮次',
      key: 'epoch',
      render: (_, record) => `${record.current_epoch || 0} / ${record.total_epochs || 0}`,
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
      width: 300,
      render: (_, record) => (
        <Space>
          <Button
            type="link"
            onClick={() => handleViewDetail(record)}
          >
            详情
          </Button>
          {record.status === 'pending' && (
            <Button
              type="link"
              icon={<PlayCircleOutlined />}
              onClick={() => handleStart(record.id)}
            >
              启动
            </Button>
          )}
          {record.status === 'running' && (
            <Button
              type="link"
              danger
              icon={<StopOutlined />}
              onClick={() => handleStop(record.id)}
            >
              停止
            </Button>
          )}
          {record.status !== 'running' && (
            <Popconfirm
              title="确定要删除这个任务吗？"
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
          )}
        </Space>
      ),
    },
  ]

  return (
    <div style={{ padding: '24px' }}>
      <Card
        title="训练任务管理"
        extra={
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => setModalVisible(true)}
          >
            创建任务
          </Button>
        }
      >
        <Table
          columns={columns}
          dataSource={tasks}
          rowKey="id"
          loading={loading}
          pagination={{ pageSize: 10 }}
        />
      </Card>

      <Modal
        title="创建训练任务"
        open={modalVisible}
        onCancel={() => {
          setModalVisible(false)
          form.resetFields()
        }}
        onOk={() => form.submit()}
        okText="创建"
        cancelText="取消"
        width={600}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleCreate}
        >
          <Form.Item
            name="name"
            label="任务名称"
            rules={[{ required: true, message: '请输入任务名称' }]}
          >
            <Input placeholder="请输入任务名称" />
          </Form.Item>
          <Form.Item
            name="dataset_path"
            label="数据集路径"
            rules={[{ required: true, message: '请输入数据集路径' }]}
          >
            <Input placeholder="例如: /path/to/dataset/data.yaml 或 /path/to/dataset/" />
          </Form.Item>
          <Form.Item
            name="epochs"
            label="训练轮次"
            initialValue={100}
          >
            <Input type="number" />
          </Form.Item>
          <Form.Item
            name="batch_size"
            label="批次大小"
            initialValue={16}
          >
            <Input type="number" />
          </Form.Item>
          <Form.Item
            name="img_size"
            label="图片尺寸"
            initialValue={640}
          >
            <Input type="number" />
          </Form.Item>
          <Form.Item
            name="learning_rate"
            label="学习率"
            initialValue={0.01}
          >
            <Input type="number" step={0.001} />
          </Form.Item>
          <Form.Item
            name="device"
            label="设备"
            initialValue="cpu"
          >
            <Input placeholder="cpu 或 cuda" />
          </Form.Item>
        </Form>
      </Modal>

      <Modal
        title="训练任务详情"
        open={detailVisible}
        onCancel={() => {
          setDetailVisible(false)
          setSelectedTask(null)
        }}
        footer={null}
        width={800}
      >
        {selectedTask && (
          <TrainingProgress task={selectedTask} />
        )}
      </Modal>
    </div>
  )
}

export default TrainingPage

