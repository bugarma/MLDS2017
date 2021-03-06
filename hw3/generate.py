import tensorflow as tf
import numpy as np
import model_ref as model
import argparse
import shutil
import os
import scipy.misc
import skipthoughts


def test_data(text_path):
    encoder = skipthoughts.Encoder(skipthoughts.load_model())

    testing_text = open(text_path).read().strip().split('\n')

    ids = []
    texts = []
    for line in testing_text:
        line = line.split(',')
        id = line[0]
        text = line[1]

        for i in range(5):
            ids.append((id, i))
            texts.append(text)

    captions = encoder.encode(texts)

    return ids, captions


def test(text_path):
    z_dim = 100
    t_dim = 256
    image_size = 64
    gf_dim = 64
    df_dim = 64
    gfc_dim = 1024
    caption_vector_length = 2400

    def save_for_vis(ids, sample):
        save_dir = './samples'

        if os.path.exists(save_dir):
            shutil.rmtree(save_dir)
        os.mkdir(save_dir)

        for i, (id, img) in enumerate(zip(ids, sample)):
            testing_id, sample_id = id
            scipy.misc.imsave(os.path.join(save_dir, 'sample_%s_%s.jpg' % (testing_id, sample_id+1)), img)

    ids, caps = test_data(text_path)
    caps = caps[:, :caption_vector_length]

    options = {
        'z_dim': z_dim,
        't_dim': t_dim,
        'image_size': image_size,
        'gf_dim': gf_dim,
        'df_dim': df_dim,
        'gfc_dim': gfc_dim,
        'caption_vector_length': caption_vector_length,
        'batch_size': len(caps)
    }

    gan = model.GAN(options)
    input_tensors, outputs = gan.build_generator()

    config = tf.ConfigProto(
                device_count = {'GPU': 0}
            )
    with tf.Session(config=config) as sess:
        saver = tf.train.Saver()
        path = tf.train.latest_checkpoint('trained_model')
        saver.restore(sess, path)

        z_noise = np.random.normal(0, 1, [len(caps), z_dim])
        feed = {
            input_tensors['t_real_caption']: caps,
            input_tensors['t_z']: z_noise
        }
        images = sess.run(outputs['generator'], feed_dict=feed)

        save_for_vis(ids, images)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("text_path")

    args = parser.parse_args()
    text_path = args.text_path

    test(text_path)