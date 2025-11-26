import axios from 'axios'

const API_BASE_URL = '/api/v1'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
})

// 文件上传
export const uploadImage = async (file) => {
  const formData = new FormData()
  formData.append('file', file)
  
  const response = await api.post('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return response.data
}

// 瑕疵检测
export const detectDefects = async (imagePath) => {
  const response = await api.post('/detect', {
    image_path: imagePath,
  })
  return response.data
}

// 瑕疵分割
export const segmentImage = async (imagePath) => {
  const response = await api.post('/segment', {
    image_path: imagePath,
  })
  return response.data
}

// LabelStudio API
export const getLabelStudioProjects = async () => {
  const response = await api.get('/labelstudio/projects')
  return response.data
}

export const createLabelStudioProject = async (projectData) => {
  const response = await api.post('/labelstudio/projects', projectData)
  return response.data
}

export const deleteLabelStudioProject = async (projectId) => {
  const response = await api.delete(`/labelstudio/projects/${projectId}`)
  return response.data
}

export const getLabelStudioProjectUrl = async (projectId) => {
  const response = await api.get(`/labelstudio/projects/${projectId}/url`)
  return response.data
}

export const exportLabelStudioProject = async (projectId, exportType = 'YOLO') => {
  const response = await api.get(`/labelstudio/projects/${projectId}/export`, {
    params: { export_type: exportType },
    responseType: 'blob'
  })
  return response.data
}

// Training API
export const getTrainingTasks = async () => {
  const response = await api.get('/training/tasks')
  return response.data
}

export const getTrainingTask = async (taskId) => {
  const response = await api.get(`/training/tasks/${taskId}`)
  return response.data
}

export const createTrainingTask = async (taskData) => {
  const response = await api.post('/training/tasks', taskData)
  return response.data
}

export const startTraining = async (taskId) => {
  const response = await api.post(`/training/tasks/${taskId}/start`)
  return response.data
}

export const stopTraining = async (taskId) => {
  const response = await api.post(`/training/tasks/${taskId}/stop`)
  return response.data
}

export const deleteTrainingTask = async (taskId) => {
  const response = await api.delete(`/training/tasks/${taskId}`)
  return response.data
}

export const uploadDataset = async (file) => {
  const formData = new FormData()
  formData.append('file', file)
  const response = await api.post('/training/datasets/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return response.data
}

// Model API
export const getModels = async () => {
  const response = await api.get('/model/models')
  return response.data
}

export const getActiveModel = async () => {
  const response = await api.get('/model/models/active')
  return response.data
}

export const uploadModel = async (file, name, description, trainingTaskId) => {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('name', name)
  if (description) formData.append('description', description)
  if (trainingTaskId) formData.append('training_task_id', trainingTaskId)
  
  const response = await api.post('/model/models/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return response.data
}

export const activateModel = async (modelId) => {
  const response = await api.post(`/model/models/${modelId}/activate`)
  return response.data
}

export const deleteModel = async (modelId) => {
  const response = await api.delete(`/model/models/${modelId}`)
  return response.data
}

export const downloadModel = async (modelId) => {
  const response = await api.get(`/model/models/${modelId}/download`, {
    responseType: 'blob'
  })
  return response.data
}

export const updateModelMetadata = async (modelId, metadata) => {
  const response = await api.patch(`/model/models/${modelId}`, metadata)
  return response.data
}

export default api

