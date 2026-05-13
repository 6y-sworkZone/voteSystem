import React, { useState } from 'react';
import { Form, Input, Button, Card, Typography, DatePicker, Space, message } from 'antd';
import { PlusOutlined, MinusCircleOutlined } from '@ant-design/icons';
import { pollAPI } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import dayjs from 'dayjs';

const { Title } = Typography;
const { TextArea } = Input;

const CreatePoll: React.FC = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();

  React.useEffect(() => {
    if (!isAuthenticated) {
      message.error('请先登录');
      navigate('/login');
    }
  }, [isAuthenticated, navigate]);

  const onFinish = async (values: any) => {
    setLoading(true);
    try {
      const deadline = values.deadline.toISOString();
      const options = values.options.filter((opt: any) => opt && opt.text.trim());
      
      if (options.length < 2) {
        message.error('至少需要2个选项');
        setLoading(false);
        return;
      }

      await pollAPI.createPoll({
        title: values.title,
        description: values.description,
        deadline,
        options,
      });
      message.success('创建投票成功');
      navigate('/');
    } catch (error) {
      message.error('创建投票失败');
    } finally {
      setLoading(false);
    }
  };

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div style={{ padding: '24px', maxWidth: 700, margin: '0 auto' }}>
      <Card>
        <Title level={2} style={{ textAlign: 'center', marginBottom: 32 }}>
          创建投票
        </Title>
        <Form form={form} name="createPoll" onFinish={onFinish} layout="vertical">
          <Form.Item
            name="title"
            label="投票标题"
            rules={[{ required: true, message: '请输入投票标题' }]}
          >
            <Input placeholder="请输入投票标题" />
          </Form.Item>
          <Form.Item name="description" label="投票描述">
            <TextArea rows={3} placeholder="请输入投票描述（可选）" />
          </Form.Item>
          <Form.Item
            name="deadline"
            label="截止时间"
            rules={[{ required: true, message: '请选择截止时间' }]}
          >
            <DatePicker
              showTime
              style={{ width: '100%' }}
              placeholder="选择截止时间"
              minDate={dayjs()}
            />
          </Form.Item>
          <Form.List
            name="options"
            initialValue={[{ text: '' }, { text: '' }]}
            rules={[
              {
                validator: async (_, options) => {
                  if (options && options.filter((opt: any) => opt && opt.text.trim()).length >= 2) {
                    return Promise.resolve();
                  }
                  return Promise.reject(new Error('至少需要2个选项'));
                },
              },
            ]}
          >
            {(fields, { add, remove }, { errors }) => (
              <>
                <div style={{ marginBottom: 16 }}>
                  <strong>投票选项</strong>
                </div>
                {fields.map((field, index) => (
                  <Form.Item key={field.key}>
                    <Space>
                      <Form.Item
                        {...field}
                        name={[field.name, 'text']}
                        rules={[{ required: true, message: '请输入选项内容' }]}
                        noStyle
                      >
                        <Input placeholder={`选项 ${index + 1}`} style={{ width: 400 }} />
                      </Form.Item>
                      {fields.length > 2 && (
                        <MinusCircleOutlined
                          onClick={() => remove(field.name)}
                          style={{ color: '#ff4d4f' }}
                        />
                      )}
                    </Space>
                  </Form.Item>
                ))}
                <Form.Item>
                  <Button
                    type="dashed"
                    onClick={() => add()}
                    icon={<PlusOutlined />}
                    style={{ width: '100%' }}
                  >
                    添加选项
                  </Button>
                  <Form.ErrorList errors={errors} />
                </Form.Item>
              </>
            )}
          </Form.List>
          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading} style={{ width: '100%' }}>
              创建投票
            </Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
};

export default CreatePoll;
