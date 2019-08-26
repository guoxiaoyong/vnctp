#include <string>
#include <queue>
#include <thread>
#include <mutex>
#include <iostream>
#include <condition_variable>

#include "pybind11/pybind11.h"


using namespace std;
using namespace pybind11;


//任务结构体
struct Task
{
    int task_name;    //回调函数名称对应的常量
    void *task_data;  //数据指针
    void *task_error; //错误指针
    int task_id;    //请求id
    bool task_last;   //是否为最后返回
};

class TerminatedError : std::exception
{};

class TaskQueue
{
private:
    queue<Task> queue_;           //标准库队列
    mutex mutex_;             //互斥锁
    condition_variable cond_;       //条件变量

    bool _terminate = false;

public:

    //存入新的任务
    void push(const Task &task)
    {
        unique_lock<mutex > mlock(mutex_);
        queue_.push(task);          //向队列中存入数据
        mlock.unlock();           //释放锁
        cond_.notify_one();         //通知正在阻塞等待的线程
    }

    //取出老的任务
    Task pop()
    {
        unique_lock<mutex> mlock(mutex_);
        cond_.wait(mlock, [&]() {
            return !queue_.empty() || _terminate;
        });       //等待条件变量通知
        if (_terminate)
            throw TerminatedError();
        Task task = queue_.front();     //获取队列中的最后一个任务
        queue_.pop();           //删除该任务
        return task;            //返回该任务
    }

    void terminate()
    {
        _terminate = true;
        cond_.notify_all();         //通知正在阻塞等待的线程
    }
};


//从字典中获取某个建值对应的整数，并赋值到请求结构体对象的值上
inline void getInt(const dict &d, const char *key, int *value)
{
    if (d.contains(key))    //检查字典中是否存在该键值
    {
        object o = d[key];    //获取该键值
        *value = o.cast<int>();
    }
};


//从字典中获取某个建值对应的浮点数，并赋值到请求结构体对象的值上
inline void getDouble(const dict &d, const char *key, double *value)
{
    if (d.contains(key))
    {
        object o = d[key];
        *value = o.cast<double>();
    }
};


//从字典中获取某个建值对应的字符，并赋值到请求结构体对象的值上
inline void getChar(const dict &d, const char *key, char *value)
{
    if (d.contains(key))
    {
        object o = d[key];
        *value = o.cast<char>();
    }
};


template <size_t size>
using string_literal = char[size];

//从字典中获取某个建值对应的字符串，并赋值到请求结构体对象的值上
template <size_t size>
void getString(const pybind11::dict &d, const char *key, string_literal<size> &value)
{
    if (d.contains(key))
    {
        object o = d[key];
        string s = o.cast<string>();
        const char *buf = s.c_str();
        strcpy(value, buf);
    }
};


//将GBK编码的字符串转换为UTF8
inline string toUtf(const string &gb2312)
{
  PyObject* unicode = PyUnicode_Decode(gb2312.data(), gb2312.size(), "GBK", "strict");
  PyObject* utf8_bytes = PyUnicode_AsUTF8String(unicode);
  string res(PyBytes_AsString(utf8_bytes), PyBytes_Size(utf8_bytes));
  return res;
}
