# -*- coding: utf-8 -*-

from bpy.types import PropertyGroup
from bpy.props import StringProperty, IntProperty, BoolProperty, FloatProperty, FloatVectorProperty

from mmd_tools import register_wrap
from mmd_tools.core.bone import FnBone

def _updateMMDBoneAdditionalTransform(prop, context):
    prop['is_additional_transform_dirty'] = True
    p_bone = context.active_pose_bone
    if p_bone and p_bone.mmd_bone.as_pointer() == prop.as_pointer():
        FnBone.apply_additional_transformation(prop.id_data)

def _updateAdditionalTransformInfluence(prop, context):
    p_bone = context.active_pose_bone
    if p_bone and p_bone.mmd_bone.as_pointer() == prop.as_pointer():
        FnBone(p_bone).update_additional_transform_influence()
    else:
        prop['is_additional_transform_dirty'] = True

def _getAdditionalTransformBone(prop):
    arm = prop.id_data
    bone_id = prop.get('additional_transform_bone_id', -1)
    if bone_id < 0:
        return ''
    fnBone = FnBone.from_bone_id(arm, bone_id)
    if not fnBone:
        return ''
    return fnBone.pose_bone.name

def _setAdditionalTransformBone(prop, value):
    arm = prop.id_data
    prop['is_additional_transform_dirty'] = True
    if value not in arm.pose.bones.keys():
        prop['additional_transform_bone_id'] = -1
        return
    pose_bone = arm.pose.bones[value]
    bone = FnBone(pose_bone)
    prop['additional_transform_bone_id'] = bone.bone_id

@register_wrap
class MMDBone(PropertyGroup):
    name_j = StringProperty(
        name='Name',
        description='Japanese Name',
        default='',
        )

    name_e = StringProperty(
        name='Name(Eng)',
        description='English Name',
        default='',
        )

    bone_id = IntProperty(
        name='Bone ID',
        default=-1,
        )

    transform_order = IntProperty(
        name='Transform Order',
        description='Deformation tier',
        min=0,
        max=100,
        )

    is_controllable = BoolProperty(
        name='Controllable',
        description='Is controllable',
        default=True,
        )

    transform_after_dynamics = BoolProperty(
        name='After Dynamics',
        description='After physics',
        default=False,
        )

    enabled_fixed_axis = BoolProperty(
        name='Fixed Axis',
        description='Use fixed axis',
        default=False,
        )

    fixed_axis = FloatVectorProperty(
        name='Fixed Axis',
        description='Fixed axis',
        subtype='XYZ',
        size=3,
        precision=3,
        step=0.1, # 0.1 / 100
        default=[0, 0, 0],
        )

    enabled_local_axes = BoolProperty(
        name='Local Axes',
        description='Use local axes',
        default=False,
        )

    local_axis_x = FloatVectorProperty(
        name='Local X-Axis',
        description='Local x-axis',
        subtype='XYZ',
        size=3,
        precision=3,
        step=0.1,
        default=[1, 0, 0],
        )

    local_axis_z = FloatVectorProperty(
        name='Local Z-Axis',
        description='Local z-axis',
        subtype='XYZ',
        size=3,
        precision=3,
        step=0.1,
        default=[0, 0, 1],
        )

    is_tip = BoolProperty(
        name='Tip Bone',
        description='Is zero length bone',
        default=False,
        )

    ik_rotation_constraint = FloatProperty(
        name='IK Rotation Constraint',
        description='The unit angle of IK',
        subtype='ANGLE',
        soft_min=0,
        soft_max=4,
        default=1,
        )

    has_additional_rotation = BoolProperty(
        name='Additional Rotation',
        description='Additional rotation',
        default=False,
        update=_updateMMDBoneAdditionalTransform,
        )

    has_additional_location = BoolProperty(
        name='Additional Location',
        description='Additional location',
        default=False,
        update=_updateMMDBoneAdditionalTransform,
        )

    additional_transform_bone = StringProperty(
        name='Additional Transform Bone',
        description='Additional transform bone',
        set=_setAdditionalTransformBone,
        get=_getAdditionalTransformBone,
        update=_updateMMDBoneAdditionalTransform,
        )

    additional_transform_bone_id = IntProperty(
        name='Additional Transform Bone ID',
        default=-1,
        update=_updateMMDBoneAdditionalTransform,
        )

    additional_transform_influence = FloatProperty(
        name='Additional Transform Influence',
        description='Additional transform influence',
        default=1,
        soft_min=-1,
        soft_max=1,
        update=_updateAdditionalTransformInfluence,
        )

    is_additional_transform_dirty = BoolProperty(
        name='',
        default=True
        )


def _mmd_ik_toggle_get(prop):
    return prop.get('mmd_ik_toggle', True)

def _mmd_ik_toggle_set(prop, v):
    #FIXME animation is not working well on Blender 2.8. Using driver is another way but it's troublesome.
    if v != prop.get('mmd_ik_toggle', None):
        prop['mmd_ik_toggle'] = v
        #print('_mmd_ik_toggle_set', v, prop.name)
        for b in prop.id_data.pose.bones:
            for c in b.constraints:
                if c.type == 'IK' and c.subtarget == prop.name:
                    #print('   ', b.name, c.name)
                    c.influence = v
                    __update_mmd_ik_chain(b if c.use_tail else b.parent, v, c.chain_count)

def __update_mmd_ik_chain(bone, enable, chain_count):
    for i in range(chain_count):
        for c in bone.constraints:
            if c.name.startswith('mmd_ik_limit'):
                #print('    -', bone.name, c.name)
                c.influence = enable
        bone = bone.parent

class _MMDPoseBoneProp:
    mmd_ik_toggle = BoolProperty(
        name='MMD IK Toggle',
        description='MMD IK toggle is used to import/export animation of IK on-off',
        get=_mmd_ik_toggle_get,
        set=_mmd_ik_toggle_set,
        )

