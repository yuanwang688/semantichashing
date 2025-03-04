import sys
sys.path.append('../')
sys.path.append('./Models/')
sys.path.append('../Utils/')

import cPickle
import gzip

from VAE_eval_script import eval_autoencoder_hashlookup_precision_recall

eval_autoencoder_hashlookup_precision_recall('VAE_beta_approx_log', './results/test_model_beta_log_L12_Noise1/', n_latent=12, prior_noise_level=1, visual_flag=False, Limit=2500)
eval_autoencoder_hashlookup_precision_recall('VAE_beta_approx_log', './results/test_model_beta_log_L12_Noise2/', n_latent=12, prior_noise_level=2, visual_flag=False, Limit=2500)
eval_autoencoder_hashlookup_precision_recall('VAE_beta_approx_log', './results/test_model_beta_log_L12_Noise10/', n_latent=12, prior_noise_level=10, visual_flag=False, Limit=2500)
eval_autoencoder_hashlookup_precision_recall('VAE_beta_approx_log', './results/test_model_beta_log_L12_Noise20/', n_latent=12, prior_noise_level=20, visual_flag=False, Limit=2500)
eval_autoencoder_hashlookup_precision_recall('VAE_beta_approx_log', './results/test_model_beta_log_L12_Noise100/', n_latent=12, prior_noise_level=100, visual_flag=False, Limit=2500)
eval_autoencoder_hashlookup_precision_recall('VAE_beta_approx_log', './results/test_model_beta_log_L12_Noise200/', n_latent=12, prior_noise_level=200, visual_flag=False, Limit=2500)
# eval_autoencoder_hashlookup_precision_recall('VAE_beta_approx', './results/test_model_beta_L12_Noise1000/', n_latent=12, prior_noise_level=1000, visual_flag=False, Limit=2500)

eval_autoencoder_hashlookup_precision_recall('VAE_beta_approx_log', './results/test_model_beta_log_L6_Noise1/', n_latent=6, prior_noise_level=1, visual_flag=False, Limit=2500)
eval_autoencoder_hashlookup_precision_recall('VAE_beta_approx_log', './results/test_model_beta_log_L6_Noise2/', n_latent=6, prior_noise_level=2, visual_flag=False, Limit=2500)
eval_autoencoder_hashlookup_precision_recall('VAE_beta_approx_log', './results/test_model_beta_log_L6_Noise10/', n_latent=6, prior_noise_level=10, visual_flag=False, Limit=2500)
eval_autoencoder_hashlookup_precision_recall('VAE_beta_approx_log', './results/test_model_beta_log_L6_Noise20/', n_latent=6, prior_noise_level=20, visual_flag=False, Limit=2500)
eval_autoencoder_hashlookup_precision_recall('VAE_beta_approx_log', './results/test_model_beta_log_L6_Noise100/', n_latent=6, prior_noise_level=100, visual_flag=False, Limit=2500)
eval_autoencoder_hashlookup_precision_recall('VAE_beta_approx_log', './results/test_model_beta_log_L6_Noise200/', n_latent=6, prior_noise_level=200, visual_flag=False, Limit=2500)
# eval_autoencoder_hashlookup_precision_recall('VAE_beta_approx', './results/test_model_beta_L6_Noise1000/', n_latent=6, prior_noise_level=1000, visual_flag=False, Limit=2500)
