import React from 'react';
import { Layout, Menu, Button } from 'antd';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const { Header } = Layout;

const Navbar: React.FC = () => {
  const { isAuthenticated, user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <Header style={{ display: 'flex', alignItems: 'center', padding: '0 24px' }}>
      <div style={{ color: 'white', fontSize: '20px', fontWeight: 'bold', marginRight: '48px' }}>
        在线投票系统
      </div>
      <Menu
        theme="dark"
        mode="horizontal"
        defaultSelectedKeys={['1']}
        style={{ flex: 1, minWidth: 0 }}
        items={[
          { key: '1', label: <Link to="/">投票列表</Link> },
          isAuthenticated && { key: '2', label: <Link to="/create">创建投票</Link> },
        ].filter(Boolean)}
      />
      <div style={{ marginLeft: 'auto' }}>
        {isAuthenticated ? (
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <span style={{ color: 'white' }}>欢迎, {user?.username}</span>
            <Button onClick={handleLogout}>退出</Button>
          </div>
        ) : (
          <div style={{ display: 'flex', gap: '8px' }}>
            <Link to="/login">
              <Button type="primary">登录</Button>
            </Link>
            <Link to="/register">
              <Button>注册</Button>
            </Link>
          </div>
        )}
      </div>
    </Header>
  );
};

export default Navbar;
