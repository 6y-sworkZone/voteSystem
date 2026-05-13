import React, { useEffect, useState } from 'react';
import { Card, List, Progress, Button, Select, Space, Tag, Typography, message } from 'antd';
import { pollAPI } from '../services/api';
import type { Poll } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';

const { Title, Text } = Typography;
const { Option } = Select;

const PollList: React.FC = () => {
  const [polls, setPolls] = useState<Poll[]>([]);
  const [loading, setLoading] = useState(false);
  const [sortBy, setSortBy] = useState('created_at');
  const [order, setOrder] = useState('desc');
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const loadPolls = async () => {
    setLoading(true);
    try {
      const response = await pollAPI.getPolls(sortBy, order);
      setPolls(response.data);
    } catch (error) {
      message.error('加载投票列表失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPolls();
  }, [sortBy, order]);

  const handleVote = async (pollId: number, optionId: number) => {
    if (!isAuthenticated) {
      message.error('请先登录');
      navigate('/login');
      return;
    }
    try {
      await pollAPI.vote(pollId, optionId);
      message.success('投票成功');
      loadPolls();
    } catch (error: any) {
      message.error(error.response?.data?.detail || '投票失败');
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('zh-CN');
  };

  return (
    <div style={{ padding: '24px', maxWidth: 1000, margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <Title level={2} style={{ margin: 0 }}>
          投票列表
        </Title>
        <Space>
          <Select value={sortBy} onChange={setSortBy} style={{ width: 140 }}>
            <Option value="created_at">按创建时间</Option>
            <Option value="votes">按投票数量</Option>
          </Select>
          <Select value={order} onChange={setOrder} style={{ width: 100 }}>
            <Option value="desc">降序</Option>
            <Option value="asc">升序</Option>
          </Select>
        </Space>
      </div>

      <List
        loading={loading}
        dataSource={polls}
        renderItem={(poll) => (
          <List.Item style={{ padding: 0, marginBottom: 16 }}>
            <Card
              title={
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span>{poll.title}</span>
                  <Space>
                    {poll.is_expired ? (
                      <Tag color="red">已截止</Tag>
                    ) : (
                      <Tag color="green">进行中</Tag>
                    )}
                    {poll.has_voted && <Tag color="blue">已投票</Tag>}
                  </Space>
                </div>
              }
              extra={<Text type="secondary">截止: {formatDate(poll.deadline)}</Text>}
              style={{ width: '100%' }}
            >
              {poll.description && (
                <Text type="secondary" style={{ display: 'block', marginBottom: 16 }}>
                  {poll.description}
                </Text>
              )}
              <div style={{ marginBottom: 8 }}>
                <Text strong>总票数: {poll.total_votes}</Text>
              </div>
              {poll.options.map((option) => (
                <div key={option.id} style={{ marginBottom: 12 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 }}>
                    <Text>
                      {option.text}
                      {poll.voted_option_id === option.id && (
                        <Tag color="blue" style={{ marginLeft: 8 }}>
                          我的选择
                        </Tag>
                      )}
                    </Text>
                    <Text type="secondary">
                      {option.vote_count} 票 ({option.percentage.toFixed(1)}%)
                    </Text>
                  </div>
                  <Progress percent={option.percentage} showInfo={false} />
                  {!poll.has_voted && !poll.is_expired && isAuthenticated && (
                    <Button
                      type="primary"
                      size="small"
                      onClick={() => handleVote(poll.id, option.id)}
                      style={{ marginTop: 4 }}
                    >
                      投票
                    </Button>
                  )}
                </div>
              ))}
              {!isAuthenticated && !poll.is_expired && (
                <Button type="primary" onClick={() => navigate('/login')} style={{ width: '100%' }}>
                  登录后投票
                </Button>
              )}
            </Card>
          </List.Item>
        )}
      />
    </div>
  );
};

export default PollList;
