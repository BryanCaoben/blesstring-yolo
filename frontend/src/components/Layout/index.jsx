import React, { useState } from 'react'
import { Layout, Menu } from 'antd'
import { useNavigate, useLocation } from 'react-router-dom'
import {
  ScanOutlined,
  TagOutlined,
  ExperimentOutlined,
  DatabaseOutlined,
} from '@ant-design/icons'
import './index.css'

const { Header, Sider, Content } = Layout

const AppLayout = ({ children }) => {
  const [collapsed, setCollapsed] = useState(false)
  const navigate = useNavigate()
  const location = useLocation()

  const menuItems = [
    {
      key: '/detection',
      icon: <ScanOutlined />,
      label: '瑕疵检测',
    },
    {
      key: '/annotation',
      icon: <TagOutlined />,
      label: '标注管理',
    },
    {
      key: '/training',
      icon: <ExperimentOutlined />,
      label: '模型训练',
    },
    {
      key: '/models',
      icon: <DatabaseOutlined />,
      label: '模型管理',
    },
  ]

  const handleMenuClick = ({ key }) => {
    navigate(key)
  }

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider
        collapsible
        collapsed={collapsed}
        onCollapse={setCollapsed}
        theme="dark"
      >
        <div className="logo">
          {!collapsed ? (
            <span style={{ color: '#fff', fontSize: '18px', fontWeight: 'bold' }}>
              🎸 AI平台
            </span>
          ) : (
            <span style={{ color: '#fff', fontSize: '20px' }}>🎸</span>
          )}
        </div>
        <Menu
          theme="dark"
          selectedKeys={[location.pathname]}
          mode="inline"
          items={menuItems}
          onClick={handleMenuClick}
        />
      </Sider>
      <Layout>
        <Header style={{ background: '#fff', padding: '0 24px', boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}>
          <h2 style={{ margin: '16px 0', color: '#001529' }}>
            乐器瑕疵检测与训练平台
          </h2>
        </Header>
        <Content style={{ margin: '24px', background: '#f0f2f5', minHeight: 'calc(100vh - 112px)' }}>
          {children}
        </Content>
      </Layout>
    </Layout>
  )
}

export default AppLayout

