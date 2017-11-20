import bpy
from mathutils import Vector, Color, Euler
import numpy

class TransientRenderEngine(bpy.types.RenderEngine):
    bl_idname = 'transient_renderer'
    bl_label = 'Transient Image Renderer'
    bl_use_preview = True

    def render(self, scene):
        
        scale = scene.render.resolution_percentage / 100.0
        self.size_x = int(scene.render.resolution_x * scale)
        self.size_y = int(scene.render.resolution_y * scale)
        self.pixel_count = self.size_x * self.size_y

        if scene.name == 'preview':
            self.render_preview(scene)
        else:
            self.render_scene(scene)

    def render_preview(self, scene):
        result = self.begin_result(0, 0, width, height)
        layer = result.layers[0].passes["Combined"]
        layer.rect = [[1., 1., 1., 1.]] * self.pixel_count
        self.end_result(result)


    def render_scene(self, scene):

        #import pdb; pdb.set_trace()
        
        times = numpy.zeros([self.size_y, self.size_x])
        colors = []

        # generate rays
        for i in range(self.size_y):
            for j in range(self.size_x):
                # generate distances from camera to lighting by bouncing through scene
                point, ray = self.calc_inital(scene.camera, i, j)
                time, color = raytrace(point, ray, scene)
                times[i, j] = time
                colors.append(color)
                #self.update_progress(float(i/height+j/width)/float(pixel_count))

        result = self.begin_result(0, 0, self.size_x, self.size_y)
        layer = result.layers[0].passes["Combined"]
        layer.rect = colors
        self.end_result(result)
    
    def calc_inital(self, camera, i, j):
        point = camera.location
        ray = Vector((j - self.size_x/2, i - self.size_y/2, 0))
        return point, ray

def raytrace(point, direction, scene):
    """ get color as a function of time (implicit function of space)
    assumes gaussian pulse of ~ 10 picoseconds
    """
    return sum(point), [1.,1.,1.,1.]
    
    

def register():
    # Register the RenderEngine
    bpy.utils.register_class(TransientRenderEngine)

    # RenderEngines also need to tell UI Panels that they are compatible
    # Otherwise most of the UI will be empty when the engine is selected.
    # In this example, we need to see the main render image button and
    # the material preview panel.
    from bl_ui import (
            properties_render,
            properties_material,
            )
    properties_render.RENDER_PT_render.COMPAT_ENGINES.add(TransientRenderEngine.bl_idname)
    properties_material.MATERIAL_PT_preview.COMPAT_ENGINES.add(TransientRenderEngine.bl_idname)


def unregister():
    bpy.utils.unregister_class(TransientRenderEngine)

    from bl_ui import (
            properties_render,
            properties_material,
            )
    properties_render.RENDER_PT_render.COMPAT_ENGINES.remove(TransientRenderEngine.bl_idname)
    properties_material.MATERIAL_PT_preview.COMPAT_ENGINES.remove(TransientRenderEngine.bl_idname)


if __name__ == "__main__":
    register()