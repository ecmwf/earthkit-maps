
from magpye.charts import Chart


class Subplots(Chart):

    def __init__(self, *args, rows=None, cols=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        self._rows = rows
        self._cols = cols
    
    @property
    def ax(self):
        if self._ax is None:
            self._ax = self.fig.add_subplot(self._rows, self._cols, 1, projection=self.crs)
            if self.bounds is not None:
                self._ax.set_extent(self.bounds, crs=self.crs)
        return self._ax