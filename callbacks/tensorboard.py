import numpy as np

class TensorBoard(object):

    def __init__(self, every, tb_sw):
        self.every = every
        self.tb_sw = tb_sw

    def __call__(self, epoch, batch, step, model, dataloaders, losses, optimizer, data, stats):

        if step % self.every == 0:

            if step < 3:  # todo grapher not working
                self.tb_sw.add_graph(model(data['inputs']), data['inputs'])

            for name, param in model.named_parameters():
                self.tb_sw.add_histogram(tag=name, values=param.clone().cpu().data.numpy(), global_step=step)

            for k, v in stats.items():
                if k != 'sample_losses':
                    self.tb_sw.add_scalar(tag=k, scalar_value=v, global_step=step)

            if hasattr(losses['train'], 'variances'):
                self.tb_sw.add_scalar(tag='variances', scalar_value=losses['train'].variances[-1], global_step=step)


class EmbeddingGrapher(object):

    def __init__(self, every, tb_sw, tag, label_image=False):
        self.every = every
        self.tb_sw = tb_sw
        self.tag = tag
        self.label_image = label_image

    def __call__(self, epoch, batch, step, model, dataloaders, losses, optimizer, data, stats):

        if step % self.every == 0:
            inputs = data['inputs']
            outputs = data['outputs'].cpu().detach().numpy()
            labels = data['labels'].cpu().detach().numpy()

            if hasattr(losses['train'], 'reps'):
                reps = losses['train'].reps.data.cpu().detach().numpy()
                outputs = np.vstack((outputs, reps))

                N = losses['train'].N
                k = losses['train'].k
                rep_labels = ['R%d_%d' % (i, j) for i in range(N) for j in range(k)]
                labels = list(labels)+rep_labels
                self.label_image = False

            if self.label_image:
                self.tb_sw.add_embedding(outputs, metadata=labels, label_img=inputs, global_step=step, tag=self.tag)
            else:
                self.tb_sw.add_embedding(outputs, metadata=labels, global_step=step, tag=self.tag)
