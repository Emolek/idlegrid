# Generated by the protocol buffer compiler.  DO NOT EDIT!

from google.protobuf import descriptor
from google.protobuf import message
from google.protobuf import reflection
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)



DESCRIPTOR = descriptor.FileDescriptor(
  name='config.proto',
  package='',
  serialized_pb='\n\x0c\x63onfig.proto\"\xa8\x02\n\x10\x43lientConfigInfo\x12\x11\n\tmachineId\x18\x01 \x02(\t\x12#\n\x04jobs\x18\x02 \x03(\x0b\x32\x15.ClientConfigInfo.Job\x1a\xdb\x01\n\x03Job\x12\n\n\x02id\x18\x01 \x02(\x05\x12\x11\n\tclientUrl\x18\x02 \x02(\t\x12/\n\x06status\x18\x03 \x02(\x0e\x32\x1f.ClientConfigInfo.Job.JobStatus\x12\x10\n\x08realtime\x18\x04 \x02(\x08\"r\n\tJobStatus\x12\x12\n\x0eSTATUS_RUNNING\x10\x00\x12\x16\n\x12STATUS_DOWNLOADING\x10\x01\x12\x12\n\x0eSTATUS_STOPPED\x10\x02\x12\x10\n\x0cSTATUS_ERROR\x10\x03\x12\x13\n\x0fSTATUS_FINISHED\x10\x04\"X\n\x10ServerConfigInfo\x12\r\n\x05login\x18\x01 \x02(\t\x12\x10\n\x08password\x18\x02 \x02(\t\x12#\n\x04jobs\x18\x03 \x03(\x0b\x32\x15.ClientConfigInfo.Job')



_CLIENTCONFIGINFO_JOB_JOBSTATUS = descriptor.EnumDescriptor(
  name='JobStatus',
  full_name='ClientConfigInfo.Job.JobStatus',
  filename=None,
  file=DESCRIPTOR,
  values=[
    descriptor.EnumValueDescriptor(
      name='STATUS_RUNNING', index=0, number=0,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='STATUS_DOWNLOADING', index=1, number=1,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='STATUS_STOPPED', index=2, number=2,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='STATUS_ERROR', index=3, number=3,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='STATUS_FINISHED', index=4, number=4,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=199,
  serialized_end=313,
)


_CLIENTCONFIGINFO_JOB = descriptor.Descriptor(
  name='Job',
  full_name='ClientConfigInfo.Job',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    descriptor.FieldDescriptor(
      name='id', full_name='ClientConfigInfo.Job.id', index=0,
      number=1, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='clientUrl', full_name='ClientConfigInfo.Job.clientUrl', index=1,
      number=2, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='status', full_name='ClientConfigInfo.Job.status', index=2,
      number=3, type=14, cpp_type=8, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='realtime', full_name='ClientConfigInfo.Job.realtime', index=3,
      number=4, type=8, cpp_type=7, label=2,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
    _CLIENTCONFIGINFO_JOB_JOBSTATUS,
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=94,
  serialized_end=313,
)

_CLIENTCONFIGINFO = descriptor.Descriptor(
  name='ClientConfigInfo',
  full_name='ClientConfigInfo',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    descriptor.FieldDescriptor(
      name='machineId', full_name='ClientConfigInfo.machineId', index=0,
      number=1, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='jobs', full_name='ClientConfigInfo.jobs', index=1,
      number=2, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[_CLIENTCONFIGINFO_JOB, ],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=17,
  serialized_end=313,
)


_SERVERCONFIGINFO = descriptor.Descriptor(
  name='ServerConfigInfo',
  full_name='ServerConfigInfo',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    descriptor.FieldDescriptor(
      name='login', full_name='ServerConfigInfo.login', index=0,
      number=1, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='password', full_name='ServerConfigInfo.password', index=1,
      number=2, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='jobs', full_name='ServerConfigInfo.jobs', index=2,
      number=3, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=315,
  serialized_end=403,
)

_CLIENTCONFIGINFO_JOB.fields_by_name['status'].enum_type = _CLIENTCONFIGINFO_JOB_JOBSTATUS
_CLIENTCONFIGINFO_JOB.containing_type = _CLIENTCONFIGINFO;
_CLIENTCONFIGINFO_JOB_JOBSTATUS.containing_type = _CLIENTCONFIGINFO_JOB;
_CLIENTCONFIGINFO.fields_by_name['jobs'].message_type = _CLIENTCONFIGINFO_JOB
_SERVERCONFIGINFO.fields_by_name['jobs'].message_type = _CLIENTCONFIGINFO_JOB
DESCRIPTOR.message_types_by_name['ClientConfigInfo'] = _CLIENTCONFIGINFO
DESCRIPTOR.message_types_by_name['ServerConfigInfo'] = _SERVERCONFIGINFO

class ClientConfigInfo(message.Message):
  __metaclass__ = reflection.GeneratedProtocolMessageType
  
  class Job(message.Message):
    __metaclass__ = reflection.GeneratedProtocolMessageType
    DESCRIPTOR = _CLIENTCONFIGINFO_JOB
    
    # @@protoc_insertion_point(class_scope:ClientConfigInfo.Job)
  DESCRIPTOR = _CLIENTCONFIGINFO
  
  # @@protoc_insertion_point(class_scope:ClientConfigInfo)

class ServerConfigInfo(message.Message):
  __metaclass__ = reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _SERVERCONFIGINFO
  
  # @@protoc_insertion_point(class_scope:ServerConfigInfo)

# @@protoc_insertion_point(module_scope)
